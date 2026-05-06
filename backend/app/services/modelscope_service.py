import base64
import json
from pathlib import Path
from typing import Any

import requests

from app.config import settings
from app.services import prompt_service
from app.utils.json_utils import safe_json_loads


FRAME_ANALYSIS_FALLBACK = {
    "description": "模型分析失败，使用默认描述",
    "interaction_score": 50,
    "emotion_score": 50,
    "rarity_score": 50,
    "cover_potential_score": 50,
    "suggested_clip_type": "long_tail",
    "fan_reaction_hypothesis": "需要人工确认该片段是否适合发布",
    "risk_note": "模型调用失败，建议人工复核",
}

PUBLISH_PLAN_FALLBACK = {
    "content_type": "long_tail",
    "title_options": ["这段现场直拍值得记录", "现场视角下的这一秒", "直播之外的现场感"],
    "recommended_title": "现场视角下的这一秒",
    "cover_text": "现场才看到的瞬间",
    "caption": "这段更适合做现场感记录，建议结合评论区反馈继续优化",
    "hashtags": ["小红书直拍", "现场感", "电竞现场"],
    "comment_prompt": "你们还想看哪个现场视角？",
    "recommended_publish_time": "晚间 20:00-22:00",
    "target_metric": "long_tail",
    "ai_strategy": "模型调用失败，使用默认小红书发布策略",
    "series_suggestion": "可纳入现场感系列",
}

POST_REVIEW_FALLBACK = {
    "summary": "本次内容已完成账号基准对比，可作为下一轮内容实验参考。",
    "best_signal": "优先观察收藏、评论和浏览相对基准的变化。",
    "weak_signal": "如果转粉数据为空，本次复盘不强行判断转粉效率。",
    "growth_reason": "该内容是否服务涨粉，需要结合互动质量和后续账号关注变化判断。",
    "problem_diagnosis": "建议继续补充发布后数据，提高复盘稳定性。",
    "next_action": "下一条内容优先延续表现更稳定的现场视角，并强化评论引导。",
    "next_content_experiments": ["保留现场感", "强化封面文字", "围绕评论区问题补拍"],
    "account_learning": "账号应持续记录不同内容类型的相对表现，形成发布优先级。",
    "memory_update_suggestion": {
        "strategy_summary": "继续以账号基准对比驱动内容实验。",
        "shooting_style_memory": "保留现场感和关键互动瞬间。",
        "content_direction_memory": "优先测试历史表现稳定的内容类型。",
        "audience_preference_memory": "继续观察收藏、评论和转粉信号。",
        "negative_lessons": "避免只记录泛现场画面而缺少明确看点。",
    },
}


def call_openai_compatible_chat(messages: list[dict], model_name: str, temperature: float = 0.7) -> str:
    if not settings.MODELSCOPE_API_KEY or not model_name:
        raise RuntimeError("ModelScope API key or model name is missing")
    response = requests.post(
        f"{settings.MODELSCOPE_BASE_URL.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {settings.MODELSCOPE_API_KEY}", "Content-Type": "application/json"},
        json={"model": model_name, "messages": messages, "temperature": temperature},
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"]


def encode_image_to_base64(image_path: str | Path) -> str:
    data = Path(image_path).read_bytes()
    return base64.b64encode(data).decode("utf-8")


def parse_model_json_response(response_text: str, fallback: dict) -> dict:
    parsed = safe_json_loads(response_text, fallback)
    return parsed if isinstance(parsed, dict) else fallback


def analyze_frame_with_qwen_vl(image_path: str, context: dict) -> dict:
    try:
        prompt = prompt_service.render_prompt("frame_analysis.txt", **context)
        image_b64 = encode_image_to_base64(image_path)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                ],
            }
        ]
        text = call_openai_compatible_chat(messages, settings.VISION_MODEL_NAME, temperature=0.45)
        return {**FRAME_ANALYSIS_FALLBACK, **parse_model_json_response(text, FRAME_ANALYSIS_FALLBACK)}
    except Exception:
        return FRAME_ANALYSIS_FALLBACK.copy()


def analyze_frames_with_qwen_vl(frame_paths: list[str], context: dict) -> list[dict]:
    return [analyze_frame_with_qwen_vl(path, context) for path in frame_paths]


def generate_publish_plan_with_llm(account: Any, asset: Any, clip: Any, benchmark: dict, memory_context: dict | None = None) -> dict:
    try:
        context = memory_context or {}
        prompt = prompt_service.render_prompt(
            "publish_plan_generation.txt",
            account_profile=json.dumps(context.get("account_profile", {"name": account.name, "niche": account.niche}), ensure_ascii=False),
            account_benchmark=json.dumps(context.get("account_benchmark", benchmark), ensure_ascii=False),
            historical_content_type_stats=json.dumps(context.get("historical_content_type_stats", []), ensure_ascii=False),
            recent_account_learning=json.dumps(context.get("recent_account_learning", []), ensure_ascii=False),
            asset_info=json.dumps(context.get("asset_info", {"event_name": asset.event_name, "scene_type": asset.scene_type}), ensure_ascii=False),
            clip_info=json.dumps(context.get("clip_info", {"start_time": clip.start_time, "end_time": clip.end_time}), ensure_ascii=False),
            clip_scores=json.dumps(context.get("clip_scores", {"growth_score": clip.growth_score}), ensure_ascii=False),
            target_metric=clip.target_metric,
        )
        text = call_openai_compatible_chat([{"role": "user", "content": prompt}], settings.TEXT_MODEL_NAME, temperature=0.6)
        return {**PUBLISH_PLAN_FALLBACK, **parse_model_json_response(text, PUBLISH_PLAN_FALLBACK)}
    except Exception:
        return PUBLISH_PLAN_FALLBACK.copy()


def generate_post_review_with_llm(account: Any, publish_plan: Any, post_result: Any, benchmark: dict, memory_context: dict | None = None) -> dict:
    try:
        context = memory_context or {}
        prompt = prompt_service.render_prompt(
            "post_review.txt",
            account_profile=json.dumps(context.get("account_profile", {"name": account.name, "niche": account.niche}), ensure_ascii=False),
            account_benchmark=json.dumps(context.get("account_benchmark", benchmark), ensure_ascii=False),
            historical_content_type_stats=json.dumps(context.get("historical_content_type_stats", []), ensure_ascii=False),
            recent_account_learning=json.dumps(context.get("recent_account_learning", []), ensure_ascii=False),
            publish_plan=json.dumps(context.get("publish_plan", {"title": publish_plan.title, "target_metric": publish_plan.target_metric}), ensure_ascii=False),
            post_result_metrics=json.dumps(context.get("post_result_metrics", {}), ensure_ascii=False),
            relative_lifts=json.dumps(context.get("relative_lifts", {}), ensure_ascii=False),
        )
        text = call_openai_compatible_chat([{"role": "user", "content": prompt}], settings.TEXT_MODEL_NAME, temperature=0.5)
        return {**POST_REVIEW_FALLBACK, **parse_model_json_response(text, POST_REVIEW_FALLBACK)}
    except Exception:
        return POST_REVIEW_FALLBACK.copy()


def integrate_account_memory_with_llm(current_memory: dict, memory_suggestion: dict) -> dict:
    fallback = fallback_integrate_account_memory(current_memory, memory_suggestion)
    try:
        prompt = (
            "你是 LiveMark 的账号长期记忆整理助手。请把账号当前长期记忆和本次复盘给出的更新建议整合成新的账号记忆。\n"
            "要求：\n"
            "- 只保留对后续选题、拍摄、发布和复盘有用的信息。\n"
            "- 不要简单拼接，去重、归纳、保持逻辑清楚。\n"
            "- 语言给小红书直拍 KOC 看，具体、自然、可执行。\n"
            "- 不要使用“爆款概率”“破解算法”“保证涨粉”“饭圈策略”等表达。\n"
            "- 如果新建议和原记忆冲突，优先保留经过复盘数据支持的判断，并弱化没有证据的判断。\n"
            "只输出 JSON，字段固定为：strategy_summary, shooting_style_memory, content_direction_memory, "
            "audience_preference_memory, negative_lessons。\n\n"
            f"账号当前长期记忆：{json.dumps(current_memory, ensure_ascii=False)}\n"
            f"本次复盘更新建议：{json.dumps(memory_suggestion, ensure_ascii=False)}"
        )
        text = call_openai_compatible_chat([{"role": "user", "content": prompt}], settings.TEXT_MODEL_NAME, temperature=0.4)
        parsed = parse_model_json_response(text, fallback)
        return {**fallback, **{key: value for key, value in parsed.items() if isinstance(value, str)}}
    except Exception:
        return fallback


def fallback_integrate_account_memory(current_memory: dict, memory_suggestion: dict) -> dict:
    fields = [
        "strategy_summary",
        "shooting_style_memory",
        "content_direction_memory",
        "audience_preference_memory",
        "negative_lessons",
    ]
    return {field: merge_memory_text(current_memory.get(field, ""), memory_suggestion.get(field, "")) for field in fields}


def merge_memory_text(current: str, suggestion: str) -> str:
    current = (current or "").strip()
    suggestion = (suggestion or "").strip()
    if not suggestion:
        return current
    if not current:
        return suggestion
    if suggestion in current:
        return current
    return f"{current}\n本次复盘补充：{suggestion}"
