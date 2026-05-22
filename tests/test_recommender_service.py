from src.services.recommender_service import recommend_destinations


def test_recommender_returns_destination_list() -> None:
    recommendations = recommend_destinations(budget_tier="medium", top_k=3)

    assert isinstance(recommendations, list)
    assert len(recommendations) <= 3
    assert recommendations


def test_recommender_filters_by_category_and_location() -> None:
    recommendations = recommend_destinations(
        budget_tier="medium",
        preferred_categories=["culture"],
        preferred_locations=["Gianyar"],
        top_k=5,
    )

    assert recommendations
    assert all(item["category"] == "culture" for item in recommendations)
    assert all(item["regency_city"] == "Gianyar" for item in recommendations)


def test_recommender_returns_empty_list_when_filters_have_no_matches() -> None:
    recommendations = recommend_destinations(
        budget_tier="medium",
        preferred_categories=["general"],
        preferred_locations=["Badung"],
        top_k=5,
    )

    assert recommendations == []


def test_recommender_uses_budget_tier_in_match_reasons() -> None:
    recommendations = recommend_destinations(budget_tier="low", top_k=5)

    assert recommendations
    assert all(
        "Suitable for low budget tier" in item["match_reasons"]
        for item in recommendations
    )
