from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from src.utils.constants import (
    MAX_RECOMMENDATIONS,
    SUPPORTED_CATEGORIES,
    SUPPORTED_SUB_CATEGORIES,
)


class PlanTripRequest(BaseModel):
    total_budget: int = Field(gt=0)
    duration_days: int = Field(ge=1, le=30)
    num_people: int = Field(ge=1, le=20)
    travel_type: Literal["solo", "couple", "family", "group"]
    preferred_categories: list[str] | None = None
    preferred_sub_categories: list[str] | None = None
    preferred_locations: list[str] | None = None
    top_k: int = Field(default=5, ge=1, le=MAX_RECOMMENDATIONS)

    @field_validator("preferred_categories")
    @classmethod
    def validate_categories(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        invalid = set(value) - set(SUPPORTED_CATEGORIES)
        if invalid:
            raise ValueError(f"Unsupported categories: {sorted(invalid)}")
        return value

    @field_validator("preferred_sub_categories")
    @classmethod
    def validate_sub_categories(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        invalid = set(value) - set(SUPPORTED_SUB_CATEGORIES)
        if invalid:
            raise ValueError(f"Unsupported sub-categories: {sorted(invalid)}")
        return value


class BudgetSummary(BaseModel):
    tier: Literal["low", "medium", "high"]
    budget_per_person_per_day: int
    total_budget: int


class AllocationItem(BaseModel):
    component: Literal["destination_tickets", "local_transport", "food", "buffer"]
    amount: int
    percentage: int


class BudgetAllocation(BaseModel):
    items: list[AllocationItem]
    total_allocated: int
    is_within_budget: bool


class DestinationRecommendation(BaseModel):
    destination_id: str
    name: str
    category: str
    sub_category: str
    district: str
    regency_city: str
    estimated_ticket_price: int
    estimated_ticket_total: int
    rating: float
    review_count: int
    popularity_score: float
    latitude: float
    longitude: float
    maps_url: str | None = None
    image_url: str | None = None
    score: float
    match_reasons: list[str]


class PlanTripResponse(BaseModel):
    status: Literal["success"]
    input_summary: dict[str, Any]
    budget: BudgetSummary
    budget_allocation: BudgetAllocation
    recommended_destinations: list[DestinationRecommendation]
    summary: dict[str, Any]
    warnings: list[str]


class MetadataResponse(BaseModel):
    travel_types: list[Literal["solo", "couple", "family", "group"]]
    categories: list[str]
    sub_categories: list[str]
    budget_tiers: list[Literal["low", "medium", "high"]]
    max_recommendations: int
