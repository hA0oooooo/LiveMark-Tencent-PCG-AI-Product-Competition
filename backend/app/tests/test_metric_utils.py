from app.utils.metric_utils import classify_lift, compute_lift, compute_rate, safe_divide


def test_safe_divide_handles_zero():
    assert safe_divide(10, 0) == 0
    assert safe_divide(None, 10) == 0
    assert safe_divide(10, 2) == 5


def test_rates_and_lifts():
    assert compute_rate(25, 100) == 0.25
    assert compute_lift(120, 100) == 1.2
    assert classify_lift(1.3) == "高于账号基准"
    assert classify_lift(0.9) == "接近账号基准"
    assert classify_lift(0.5) == "低于账号基准"
