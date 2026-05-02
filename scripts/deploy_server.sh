#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/livemark}"
SERVER_NAME="${SERVER_NAME:-124.223.117.70}"

cd "$APP_DIR"

echo "[LiveMark] Checking root .env..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "[LiveMark] Created .env from .env.example."
  echo "[LiveMark] Edit /opt/livemark/.env and set MODELSCOPE_API_KEY before rerunning this script."
  exit 1
fi

if grep -q "YOUR_DASHSCOPE_API_KEY" .env; then
  echo "[LiveMark] .env still contains YOUR_DASHSCOPE_API_KEY."
  echo "[LiveMark] Edit /opt/livemark/.env with the real DashScope API Key, then rerun this script."
  exit 1
fi

set -a
. "$APP_DIR/.env"
set +a

echo "[LiveMark] Preparing backend..."
cd "$APP_DIR/backend"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m app.seed

echo "[LiveMark] Building frontend..."
cd "$APP_DIR/frontend"
npm install
npm run build

echo "[LiveMark] Starting services with PM2..."
cd "$APP_DIR"
pm2 delete livemark-backend >/dev/null 2>&1 || true
pm2 delete livemark-frontend >/dev/null 2>&1 || true
pm2 start "$APP_DIR/backend/.venv/bin/python" \
  --name livemark-backend \
  --cwd "$APP_DIR/backend" \
  -- -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pm2 start npm \
  --name livemark-frontend \
  --cwd "$APP_DIR/frontend" \
  -- run start -- --hostname 127.0.0.1 --port 3000
pm2 save

echo "[LiveMark] Writing Nginx config..."
sudo tee /etc/nginx/sites-available/livemark >/dev/null <<NGINX
server {
    listen 80;
    server_name ${SERVER_NAME};

    client_max_body_size 200m;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /uploads/ {
        proxy_pass http://127.0.0.1:8000/uploads/;
        proxy_set_header Host \$host;
    }

    location /frames/ {
        proxy_pass http://127.0.0.1:8000/frames/;
        proxy_set_header Host \$host;
    }

    location /clips/ {
        proxy_pass http://127.0.0.1:8000/clips/;
        proxy_set_header Host \$host;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/livemark /etc/nginx/sites-enabled/livemark
sudo nginx -t
sudo systemctl reload nginx

echo "[LiveMark] Deployment complete."
echo "[LiveMark] Open: http://${SERVER_NAME}/dashboard"
