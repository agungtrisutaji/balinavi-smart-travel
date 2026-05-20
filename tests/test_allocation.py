from src.services.allocation_service import allocate_budget


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
