from fastapi.testclient import TestClient

from app.backend.core.config import APP_VERSION
from app.backend.main import app


client = TestClient(app)


def test_health_returns_status_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "balinavi-backend",
        "version": APP_VERSION,
    }


def test_metadata_returns_supported_options() -> None:
    response = client.get("/metadata")

    assert response.status_code == 200
    data = response.json()
    assert data["travel_types"] == ["solo", "couple", "family", "group"]
    assert data["budget_tiers"] == ["low", "medium", "high"]
    assert data["max_recommendations"] == 10


def test_plan_trip_returns_documented_fields() -> None:
    payload = {
        "total_budget": 5_000_000,
        "duration_days": 3,
        "num_people": 2,
        "travel_type": "family",
        "preferred_categories": ["nature", "culture"],
        "preferred_sub_categories": ["beach", "temple"],
        "preferred_locations": ["Badung", "Gianyar"],
        "top_k": 5,
    }

    response = client.post("/plan-trip", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {
        "status",
        "input_summary",
        "budget",
        "budget_allocation",
        "recommended_destinations",
        "summary",
        "warnings",
    }
    assert data["status"] == "success"
    assert data["budget"]["tier"] in {"low", "medium", "high"}
    assert data["budget_allocation"]["total_allocated"] <= payload["total_budget"]
    assert data["summary"]["remaining_budget"] >= 0
    assert isinstance(data["recommended_destinations"], list)
