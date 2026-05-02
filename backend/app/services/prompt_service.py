from pathlib import Path


PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def render_prompt(name: str, **kwargs) -> str:
    text = load_prompt(name)
    for key, value in kwargs.items():
        text = text.replace("{" + key + "}", str(value))
    return text
