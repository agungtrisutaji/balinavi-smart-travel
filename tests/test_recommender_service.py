"""Tests for recommender_service – both dummy fallback and real model."""

from __future__ import annotations

import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

import src.services.recommender_service as svc
from src.services.recommender_service import recommend_destinations


# ---------------------------------------------------------------------------
# Helper: reset singleton state between tests
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _reset_singleton():
    """Ensure each test starts with a fresh singleton check."""
    svc._recommender_instance = None
    svc._use_real_model = None
    yield
    svc._recommender_instance = None
    svc._use_real_model = None


# ===================================================================
# Original tests (preserved for backward compatibility)
# ===================================================================

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
    # Force dummy mode so the "no matches" assertion works predictably
    svc._use_real_model = False
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
    for item in recommendations:
        reasons_text = " ".join(item["match_reasons"]).lower()
        assert "low" in reasons_text or "budget" in reasons_text


# ===================================================================
# New tests for real model integration
# ===================================================================

def test_recommender_fallback_to_dummy_when_no_artifacts() -> None:
    """When artifacts are absent, service must still work using dummy data."""
    with patch.object(svc, "_artifacts_available", return_value=False):
        svc._recommender_instance = None
        svc._use_real_model = None

        recs = recommend_destinations(budget_tier="medium", top_k=3)

    assert isinstance(recs, list)
    assert len(recs) <= 3
    # Dummy IDs start with "DUMMY-"
    assert all(r["destination_id"].startswith("DUMMY-") for r in recs)


def test_recommender_uses_real_model_when_artifacts_exist() -> None:
    """When artifacts are present, service must use ContentBasedRecommender."""
    artifacts_dir = Path(svc.ARTIFACTS_DIR)
    if not all((artifacts_dir / f).is_file() for f in svc._REQUIRED_ARTIFACTS):
        pytest.skip("Artifacts not generated yet; run training first.")

    recs = recommend_destinations(budget_tier="medium", top_k=5)

    assert isinstance(recs, list)
    assert len(recs) <= 5
    assert recs
    # Real model IDs start with "DEST-"
    assert all(r["destination_id"].startswith("DEST-") for r in recs)


def test_recommender_score_is_between_0_and_1() -> None:
    """Recommendation scores must be in [0.0, 1.0]."""
    artifacts_dir = Path(svc.ARTIFACTS_DIR)
    if not all((artifacts_dir / f).is_file() for f in svc._REQUIRED_ARTIFACTS):
        pytest.skip("Artifacts not generated yet; run training first.")

    recs = recommend_destinations(
        budget_tier="medium",
        preferred_categories=["nature"],
        top_k=5,
    )

    assert recs
    for rec in recs:
        assert 0.0 <= rec["score"] <= 1.0, f"Score out of range: {rec['score']}"


def test_recommender_returns_dynamic_match_reasons() -> None:
    """Real model must produce dynamic match_reasons with percentages."""
    artifacts_dir = Path(svc.ARTIFACTS_DIR)
    if not all((artifacts_dir / f).is_file() for f in svc._REQUIRED_ARTIFACTS):
        pytest.skip("Artifacts not generated yet; run training first.")

    recs = recommend_destinations(
        budget_tier="medium",
        preferred_categories=["nature"],
        preferred_locations=["Badung"],
        top_k=3,
    )

    assert recs
    first = recs[0]
    reasons = first["match_reasons"]
    # Must contain "Content similarity: XX%"
    assert any("Content similarity" in r for r in reasons), f"Missing similarity reason: {reasons}"
