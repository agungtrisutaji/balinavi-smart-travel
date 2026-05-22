import pytest

from src.services.allocation_service import allocate_budget, validate_allocation_rules


def test_allocation_never_exceeds_budget() -> None:
    total_budget = 5_000_001

    allocation = allocate_budget(total_budget)

    assert allocation["total_allocated"] <= total_budget
    assert allocation["is_within_budget"] is True


def test_allocation_uses_mvp_components() -> None:
    allocation = allocate_budget(5_000_000)
    components = [item["component"] for item in allocation["items"]]

    assert components == [
        "destination_tickets",
        "local_transport",
        "food",
        "buffer",
    ]


def test_allocation_rule_percentages_must_sum_to_100() -> None:
    with pytest.raises(ValueError, match="sum to 100"):
        validate_allocation_rules(
            [
                ("destination_tickets", 25),
                ("local_transport", 25),
                ("food", 30),
                ("buffer", 10),
            ]
        )


def test_allocation_rule_percentages_must_not_be_negative() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        validate_allocation_rules(
            [
                ("destination_tickets", 25),
                ("local_transport", 25),
                ("food", 60),
                ("buffer", -10),
            ]
        )
