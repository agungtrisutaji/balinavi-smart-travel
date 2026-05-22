LOW_BUDGET_LIMIT = 500_000
MEDIUM_BUDGET_LIMIT = 1_000_000


def classify_budget(
    total_budget: int,
    duration_days: int,
    num_people: int,
) -> dict:
    if total_budget <= 0:
        raise ValueError("total_budget must be greater than 0")
    if duration_days <= 0:
        raise ValueError("duration_days must be greater than 0")
    if num_people <= 0:
        raise ValueError("num_people must be greater than 0")

    budget_per_person_per_day = total_budget // (duration_days * num_people)

    if budget_per_person_per_day < LOW_BUDGET_LIMIT:
        tier = "low"
    elif budget_per_person_per_day <= MEDIUM_BUDGET_LIMIT:
        tier = "medium"
    else:
        tier = "high"

    return {
        "tier": tier,
        "budget_per_person_per_day": budget_per_person_per_day,
        "total_budget": total_budget,
    }
