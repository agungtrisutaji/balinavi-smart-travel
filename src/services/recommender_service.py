"""
Recommender service layer for BaliNavi.

Uses ContentBasedRecommender when artifacts are available,
falls back to DummyRecommender with DUMMY_DESTINATIONS otherwise.
"""

from __future__ import annotations

import logging
from pathlib import Path

from src.models.recommender import ContentBasedRecommender, DummyRecommender

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Artifacts directory
# ---------------------------------------------------------------------------
ARTIFACTS_DIR = "artifacts"
_REQUIRED_ARTIFACTS = ["vectorizer.pkl", "tfidf_matrix.pkl", "destination_data.pkl"]

# ---------------------------------------------------------------------------
# Singleton state
# ---------------------------------------------------------------------------
_recommender_instance: ContentBasedRecommender | None = None
_use_real_model: bool | None = None  # None = not yet checked

# ---------------------------------------------------------------------------
# Dummy data (backward compatibility / fallback)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Internal: lazy-load the real model or fall back to dummy
# ---------------------------------------------------------------------------
def _artifacts_available() -> bool:
    """Return True if all required artifact files exist."""
    base = Path(ARTIFACTS_DIR)
    return all((base / f).is_file() for f in _REQUIRED_ARTIFACTS)


def _get_recommender() -> ContentBasedRecommender | None:
    """Return the singleton ContentBasedRecommender or None (→ use dummy)."""
    global _recommender_instance, _use_real_model

    if _use_real_model is None:
        # First call – check artifact availability
        if _artifacts_available():
            try:
                _recommender_instance = ContentBasedRecommender.load(ARTIFACTS_DIR)
                _use_real_model = True
                logger.info("Loaded real ContentBasedRecommender from %s/", ARTIFACTS_DIR)
            except Exception:
                logger.exception("Failed to load artifacts; falling back to dummy.")
                _use_real_model = False
        else:
            logger.info("Artifacts not found in %s/; using DummyRecommender.", ARTIFACTS_DIR)
            _use_real_model = False

    return _recommender_instance if _use_real_model else None


# ---------------------------------------------------------------------------
# Dummy helpers (same as original code)
# ---------------------------------------------------------------------------
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


def _recommend_dummy(
    budget_tier: str,
    preferred_categories: list[str] | None = None,
    preferred_sub_categories: list[str] | None = None,
    preferred_locations: list[str] | None = None,
    top_k: int = 5,
) -> list[dict]:
    """Original dummy-based recommendation logic."""
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


# ---------------------------------------------------------------------------
# Public API  (signature unchanged – backward compatible with routes.py)
# ---------------------------------------------------------------------------
def recommend_destinations(
    budget_tier: str,
    preferred_categories: list[str] | None = None,
    preferred_sub_categories: list[str] | None = None,
    preferred_locations: list[str] | None = None,
    top_k: int = 5,
) -> list[dict]:
    """Return ranked destination recommendations.

    Delegates to ContentBasedRecommender when artifacts are available,
    otherwise falls back to the legacy dummy data.
    """
    recommender = _get_recommender()

    if recommender is not None:
        return recommender.recommend(
            budget_tier=budget_tier,
            preferred_categories=preferred_categories,
            preferred_sub_categories=preferred_sub_categories,
            preferred_locations=preferred_locations,
            top_k=top_k,
        )

    # Fallback → dummy
    return _recommend_dummy(
        budget_tier=budget_tier,
        preferred_categories=preferred_categories,
        preferred_sub_categories=preferred_sub_categories,
        preferred_locations=preferred_locations,
        top_k=top_k,
    )
