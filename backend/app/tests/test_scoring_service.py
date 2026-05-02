from app.services.scoring_service import compute_account_fit_score, compute_growth_score, infer_target_metric


def test_growth_score_formula():
    score = compute_growth_score(
        {
            "interaction_score": 80,
            "emotion_score": 70,
            "rarity_score": 60,
            "clarity_score": 50,
            "title_cover_score": 40,
            "account_fit_score": 90,
        }
    )
    assert score == 66.5


def test_account_fit_default():
    assert compute_account_fit_score("interaction", []) == 60


def test_target_metric_degrades_follow():
    scores = {"account_fit_score": 80, "interaction_score": 75}
    assert infer_target_metric(scores, "interaction", follows_available=True) == "follow"
    assert infer_target_metric(scores, "interaction", follows_available=False) == "comment"
