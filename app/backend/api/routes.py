from fastapi import APIRouter

from app.backend.core.config import APP_VERSION
from app.backend.schemas.trip_schema import (
    MetadataResponse,
    PlanTripRequest,
    PlanTripResponse,
)
from src.services.allocation_service import allocate_budget
from src.services.budget_service import classify_budget
from src.services.recommender_service import recommend_destinations
from src.utils.constants import (
    BUDGET_TIERS,
    MAX_RECOMMENDATIONS,
    SUPPORTED_CATEGORIES,
    SUPPORTED_SUB_CATEGORIES,
    SUPPORTED_TRAVEL_TYPES,
)

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "balinavi-backend",
        "version": APP_VERSION,
    }


@router.get("/metadata", response_model=MetadataResponse)
def get_metadata() -> MetadataResponse:
    return MetadataResponse(
        travel_types=SUPPORTED_TRAVEL_TYPES,
        categories=SUPPORTED_CATEGORIES,
        sub_categories=SUPPORTED_SUB_CATEGORIES,
        budget_tiers=BUDGET_TIERS,
        max_recommendations=MAX_RECOMMENDATIONS,
    )


@router.post("/plan-trip", response_model=PlanTripResponse)
def plan_trip(payload: PlanTripRequest) -> PlanTripResponse:
    budget = classify_budget(
        total_budget=payload.total_budget,
        duration_days=payload.duration_days,
        num_people=payload.num_people,
    )
    budget_allocation = allocate_budget(payload.total_budget)
    recommendations = recommend_destinations(
        budget_tier=budget["tier"],
        preferred_categories=payload.preferred_categories,
        preferred_sub_categories=payload.preferred_sub_categories,
        preferred_locations=payload.preferred_locations,
        top_k=payload.top_k,
    )
    remaining_budget = payload.total_budget - budget_allocation["total_allocated"]

    return PlanTripResponse(
        status="success",
        input_summary=payload.model_dump(),
        budget=budget,
        budget_allocation=budget_allocation,
        recommended_destinations=recommendations,
        summary={
            "recommended_count": len(recommendations),
            "total_estimated_cost": budget_allocation["total_allocated"],
            "remaining_budget": remaining_budget,
            "message": "Recommendation generated successfully.",
        },
        warnings=[],
    )
