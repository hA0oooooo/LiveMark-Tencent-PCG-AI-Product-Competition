def safe_divide(numerator: float | int | None, denominator: float | int | None, default: float = 0) -> float:
    if numerator is None or denominator in (None, 0):
        return default
    return float(numerator) / float(denominator)


def compute_rate(value: float | int | None, views: float | int | None) -> float:
    return safe_divide(value, views)


def compute_lift(value: float | int | None, baseline: float | int | None) -> float:
    return safe_divide(value, baseline)


def format_percentage(value: float | None) -> str:
    if value is None:
        return "暂无"
    return f"{value * 100:.1f}%"


def classify_lift(value: float | None) -> str:
    if value is None or value == 0:
        return "暂无对比"
    if value >= 1.2:
        return "高于账号基准"
    if value >= 0.8:
        return "接近账号基准"
    return "低于账号基准"
