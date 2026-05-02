import json
import re
from typing import Any


def extract_json_from_text(text: str) -> str:
    if not text:
        return "{}"
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fenced:
        return fenced.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    return text


def repair_json_like_text(text: str) -> str:
    return text.strip().replace("，", ",").replace("：", ":")


def safe_json_loads(text: str, fallback: Any) -> Any:
    try:
        return json.loads(extract_json_from_text(text))
    except Exception:
        try:
            return json.loads(repair_json_like_text(extract_json_from_text(text)))
        except Exception:
            return fallback
