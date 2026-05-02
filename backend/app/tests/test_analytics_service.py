from app.services.analytics_service import compare_post_to_baseline


def test_compare_post_to_baseline_avoids_zero():
    result = compare_post_to_baseline({"views": 100, "likes": 20, "saves": 10, "comments": 5, "follows": 1}, {})
    assert result["relative_view_lift"] == 0
    assert result["relative_like_lift"] == 0
