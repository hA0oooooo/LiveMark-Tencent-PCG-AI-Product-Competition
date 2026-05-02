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
        text = call_openai_compatible_chat(messages, settings.VISION_MODEL_NAME, temperature=0.3)
        return {**FRAME_ANALYSIS_FALLBACK, **parse_model_json_response(text, FRAME_ANALYSIS_FALLBACK)}
    except Exception:
        return FRAME_ANALYSIS_FALLBACK.copy()


def analyze_frames_with_qwen_vl(frame_paths: list[str], context: dict) -> list[dict]:
    return [analyze_frame_with_qwen_vl(path, context) for path in frame_paths]


def generate_publish_plan_with_llm(account: Any, asset: Any, clip: Any, benchmark: dict) -> dict:
    try:
        prompt = prompt_service.render_prompt(
            "publish_plan_generation.txt",
            account_profile=json.dumps({"name": account.name, "niche": account.niche}, ensure_ascii=False),
            account_benchmark=json.dumps(benchmark, ensure_ascii=False),
            historical_content_type_stats="",
            asset_info=json.dumps({"event_name": asset.event_name, "scene_type": asset.scene_type}, ensure_ascii=False),
            clip_info=json.dumps({"start_time": clip.start_time, "end_time": clip.end_time}, ensure_ascii=False),
            clip_scores=json.dumps(
                {
                    "growth_score": clip.growth_score,
                    "interaction_score": clip.interaction_score,
                    "emotion_score": clip.emotion_score,
                    "rarity_score": clip.rarity_score,
                },
                ensure_ascii=False,
            ),
            target_metric=clip.target_metric,
        )
        text = call_openai_compatible_chat([{"role": "user", "content": prompt}], settings.TEXT_MODEL_NAME, temperature=0.6)
        return {**PUBLISH_PLAN_FALLBACK, **parse_model_json_response(text, PUBLISH_PLAN_FALLBACK)}
    except Exception:
        return PUBLISH_PLAN_FALLBACK.copy()


def generate_post_review_with_llm(account: Any, publish_plan: Any, post_result: Any, benchmark: dict) -> dict:
    try:
        prompt = prompt_service.render_prompt(
            "post_review.txt",
            account_profile=json.dumps({"name": account.name, "niche": account.niche}, ensure_ascii=False),
            account_benchmark=json.dumps(benchmark, ensure_ascii=False),
            historical_content_type_stats="",
            publish_plan=json.dumps({"title": publish_plan.title, "target_metric": publish_plan.target_metric}, ensure_ascii=False),
            post_result_metrics=json.dumps(
                {
                    "views": post_result.views,
                    "likes": post_result.likes,
                    "saves": post_result.saves,
                    "comments": post_result.comments,
                    "follows": post_result.follows,
                },
                ensure_ascii=False,
            ),
            relative_lifts=json.dumps(
                {
                    "relative_view_lift": post_result.relative_view_lift,
                    "relative_like_lift": post_result.relative_like_lift,
                    "relative_save_lift": post_result.relative_save_lift,
                    "relative_comment_lift": post_result.relative_comment_lift,
                    "relative_follow_lift": post_result.relative_follow_lift,
                },
                ensure_ascii=False,
            ),
        )
        text = call_openai_compatible_chat([{"role": "user", "content": prompt}], settings.TEXT_MODEL_NAME, temperature=0.5)
        return {**POST_REVIEW_FALLBACK, **parse_model_json_response(text, POST_REVIEW_FALLBACK)}
    except Exception:
        return POST_REVIEW_FALLBACK.copy()
