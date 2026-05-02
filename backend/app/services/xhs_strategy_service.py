def get_xhs_title_style(clip_type: str, target_metric: str) -> str:
    mapping = {
        "interaction": "直播没拍到的这一秒",
        "high_quality_collection": "适合收藏反复看的高清现场",
        "emotion": "现场感拉满的情绪瞬间",
        "persona_detail": "只有现场视角才看到的小动作",
        "long_tail": "过几天还想回看的现场记录",
    }
    return mapping.get(clip_type, "现场视角下的这一秒")


def get_xhs_hashtag_suggestions(scene_type: str, clip_type: str) -> list[str]:
    base = ["小红书直拍", "现场感"]
    if scene_type:
        base.append(scene_type)
    type_tags = {
        "interaction": "现场互动",
        "high_quality_collection": "高清收藏",
        "emotion": "情绪氛围",
        "persona_detail": "人设细节",
        "long_tail": "长尾记录",
    }
    base.append(type_tags.get(clip_type, "内容实验"))
    return base


def get_xhs_comment_prompt_strategy(target_metric: str) -> str:
    mapping = {
        "comment": "你们还想看哪个现场视角？",
        "follow": "下一场还想继续看这种直拍吗？",
        "save": "这段适合反复看吗？",
        "click": "你们第一眼注意到哪里？",
        "long_tail": "过几天你还会想回看这一幕吗？",
    }
    return mapping.get(target_metric, "你们还想看哪个现场视角？")


def get_xhs_publish_window(clip_type: str) -> str:
    return "晚间 20:00-22:00" if clip_type in {"emotion", "long_tail"} else "赛后 1 小时内或晚间 20:00-22:00"


def get_xhs_growth_action(clip_type: str, target_metric: str) -> str:
    return f"围绕{get_xhs_title_style(clip_type, target_metric)}做小红书发布建议，目标指标为 {target_metric}。"


def build_fallback_plan(asset, clip) -> dict:
    hashtags = get_xhs_hashtag_suggestions(asset.scene_type, clip.clip_type)
    return {
        "content_type": clip.clip_type,
        "recommended_title": get_xhs_title_style(clip.clip_type, clip.target_metric),
        "cover_text": "现场才看到的瞬间",
        "caption": "这段直拍更适合做现场感记录，建议结合评论区反馈继续优化下一轮内容实验。",
        "hashtags": hashtags,
        "comment_prompt": get_xhs_comment_prompt_strategy(clip.target_metric),
        "recommended_publish_time": get_xhs_publish_window(clip.clip_type),
        "target_metric": clip.target_metric,
        "ai_strategy": get_xhs_growth_action(clip.clip_type, clip.target_metric),
    }
