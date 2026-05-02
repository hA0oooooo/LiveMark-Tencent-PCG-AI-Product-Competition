from types import SimpleNamespace

from app.services import memory_service


def test_account_profile_memory_has_long_term_fields():
    account = SimpleNamespace(
        name="test",
        platform="小红书",
        niche="电竞现场",
        target_audience="目标粉丝",
        style_positioning="现场感",
        follower_count=100,
        strategy_summary="策略",
        shooting_style_memory="拍法",
        content_direction_memory="内容方向",
        audience_preference_memory="粉丝偏好",
        negative_lessons="少做泛现场",
        updated_memory_at=None,
    )

    profile = memory_service.account_profile_memory(account)

    assert profile["strategy_summary"] == "策略"
    assert profile["shooting_style_memory"] == "拍法"
    assert profile["negative_lessons"] == "少做泛现场"
