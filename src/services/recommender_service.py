DUMMY_DESTINATIONS = [
    {
        "destination_id": "DUMMY-001",
        "name": "Pantai Kuta",
        "category": "nature",
        "sub_category": "beach",
        "district": "Kuta",
        "regency_city": "Badung",
        "estimated_ticket_price": 0,
        "estimated_ticket_total": 0,
        "rating": 4.5,
        "review_count": 1000,
        "popularity_score": 0.9,
        "latitude": -8.7185,
        "longitude": 115.1686,
        "maps_url": None,
        "image_url": None,
        "score": 0.92,
        "budget_tiers": ["low", "medium", "high"],
        "match_reasons": [
            "Matches preferred category",
            "Suitable for selected budget tier",
        ],
    },
    {
        "destination_id": "DUMMY-002",
        "name": "Pura Tirta Empul",
        "category": "culture",
        "sub_category": "temple",
        "district": "Tampaksiring",
        "regency_city": "Gianyar",
        "estimated_ticket_price": 50_000,
        "estimated_ticket_total": 50_000,
        "rating": 4.6,
        "review_count": 800,
        "popularity_score": 0.86,
        "latitude": -8.4159,
        "longitude": 115.3152,
        "maps_url": None,
        "image_url": None,
        "score": 0.88,
        "budget_tiers": ["medium", "high"],
        "match_reasons": [
            "Matches preferred category",
            "Matches preferred location",
        ],
    },
    {
        "destination_id": "DUMMY-003",
        "name": "Tegenungan Waterfall",
        "category": "nature",
        "sub_category": "waterfall",
        "district": "Sukawati",
        "regency_city": "Gianyar",
        "estimated_ticket_price": 25_000,
        "estimated_ticket_total": 25_000,
        "rating": 4.3,
        "review_count": 650,
        "popularity_score": 0.78,
        "latitude": -8.5755,
        "longitude": 115.2898,
        "maps_url": None,
        "image_url": None,
        "score": 0.81,
        "budget_tiers": ["low", "medium", "high"],
        "match_reasons": [
            "Matches preferred category",
            "Suitable for selected budget tier",
        ],
    },
    {
        "destination_id": "DUMMY-004",
        "name": "Garuda Wisnu Kencana",
        "category": "recreation",
        "sub_category": "landmark",
        "district": "South Kuta",
        "regency_city": "Badung",
        "estimated_ticket_price": 125_000,
        "estimated_ticket_total": 125_000,
        "rating": 4.4,
        "review_count": 900,
        "popularity_score": 0.84,
        "latitude": -8.8104,
        "longitude": 115.1676,
        "maps_url": None,
        "image_url": None,
        "score": 0.79,
        "budget_tiers": ["medium", "high"],
        "match_reasons": [
            "Matches preferred location",
            "Suitable for selected budget tier",
        ],
    },
]


def _build_match_reasons(destination: dict, budget_tier: str) -> list[str]:
    reasons = list(destination["match_reasons"])
    budget_reason = f"Suitable for {budget_tier} budget tier"
    if budget_reason not in reasons:
        reasons.append(budget_reason)
    return reasons


def _format_destination(destination: dict, budget_tier: str) -> dict:
    formatted = {
        key: value
        for key, value in destination.items()
        if key != "budget_tiers"
    }
    formatted["match_reasons"] = _build_match_reasons(destination, budget_tier)
    return formatted


def recommend_destinations(
    budget_tier: str,
    preferred_categories: list[str] | None = None,
    preferred_sub_categories: list[str] | None = None,
    preferred_locations: list[str] | None = None,
    top_k: int = 5,
) -> list[dict]:
    categories = set(preferred_categories or [])
    sub_categories = set(preferred_sub_categories or [])
    locations = set(preferred_locations or [])

    filtered = []
    for destination in DUMMY_DESTINATIONS:
        if budget_tier not in destination["budget_tiers"]:
            continue
        if categories and destination["category"] not in categories:
            continue
        if sub_categories and destination["sub_category"] not in sub_categories:
            continue
        if locations and destination["regency_city"] not in locations:
            continue
        filtered.append(destination)

    return sorted(
        [_format_destination(destination, budget_tier) for destination in filtered],
        key=lambda destination: destination["score"],
        reverse=True,
    )[:top_k]
