from src.services.budget_service import classify_budget


def test_budget_tier_low() -> None:
    result = classify_budget(total_budget=2_000_000, duration_days=3, num_people=2)

    assert result["tier"] == "low"


def test_budget_tier_medium() -> None:
    result = classify_budget(total_budget=5_000_000, duration_days=3, num_people=2)

    assert result["tier"] == "medium"


def test_budget_tier_high() -> None:
    result = classify_budget(total_budget=7_000_000, duration_days=3, num_people=2)

    assert result["tier"] == "high"


def test_budget_tier_returns_supported_values_only() -> None:
    result = classify_budget(total_budget=5_000_000, duration_days=3, num_people=2)

    assert result["tier"] in {"low", "medium", "high"}
