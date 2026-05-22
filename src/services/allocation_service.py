ALLOCATION_RULES = [
    ("destination_tickets", 25),
    ("local_transport", 25),
    ("food", 30),
    ("buffer", 20),
]


def validate_allocation_rules(allocation_rules: list[tuple[str, int]]) -> None:
    percentages = [percentage for _, percentage in allocation_rules]

    if any(percentage < 0 for percentage in percentages):
        raise ValueError("allocation percentages must not be negative")
    if sum(percentages) != 100:
        raise ValueError("allocation percentages must sum to 100")


def allocate_budget(total_budget: int) -> dict:
    if total_budget <= 0:
        raise ValueError("total_budget must be greater than 0")
    validate_allocation_rules(ALLOCATION_RULES)

    items = []
    allocated_before_last = 0

    for component, percentage in ALLOCATION_RULES[:-1]:
        amount = total_budget * percentage // 100
        allocated_before_last += amount
        items.append(
            {
                "component": component,
                "amount": amount,
                "percentage": percentage,
            }
        )

    last_component, last_percentage = ALLOCATION_RULES[-1]
    last_amount = total_budget - allocated_before_last
    items.append(
        {
            "component": last_component,
            "amount": last_amount,
            "percentage": last_percentage,
        }
    )

    total_allocated = sum(item["amount"] for item in items)

    return {
        "items": items,
        "total_allocated": total_allocated,
        "is_within_budget": total_allocated <= total_budget,
    }
