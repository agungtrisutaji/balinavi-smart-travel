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
