# API Contract - BaliNavi

## Overview

This document defines the API contract between the FastAPI backend and Streamlit frontend.

The API contract must remain stable unless the team agrees to update this document, related tests, and frontend integration.

## Base URLs

Local backend:

```text
http://localhost:8000
```

Docker Compose internal frontend-to-backend URL:

```text
http://backend:8000
```

## Endpoints

The MVP API provides:

```text
GET  /health
GET  /metadata
POST /plan-trip
```

---

## GET /health

Health check endpoint.

### Request

No request body.

### Success Response

Status code: `200`

```json
{
  "status": "ok",
  "service": "balinavi-backend",
  "version": "0.1.0"
}
```

---

## GET /metadata

Returns available options for frontend form inputs.

### Request

No request body.

### Success Response

Status code: `200`

```json
{
  "travel_types": ["solo", "couple", "family", "group"],
  "categories": ["nature", "culture", "recreation", "general"],
  "sub_categories": [
    "beach",
    "temple",
    "waterfall",
    "forest",
    "mountain",
    "museum",
    "village",
    "waterpark",
    "landmark",
    "shopping"
  ],
  "budget_tiers": ["low", "medium", "high"],
  "max_recommendations": 10
}
```

---

## POST /plan-trip

Main endpoint for generating trip recommendation and budget allocation.

### Request Body

```json
{
  "total_budget": 5000000,
  "duration_days": 3,
  "num_people": 2,
  "travel_type": "family",
  "preferred_categories": ["nature", "culture"],
  "preferred_sub_categories": ["beach", "temple"],
  "preferred_locations": ["Badung", "Gianyar"],
  "top_k": 5
}
```

### Request Fields

| Field | Type | Required | Validation |
|---|---|---:|---|
| total_budget | integer | yes | greater than 0 |
| duration_days | integer | yes | 1 to 30 |
| num_people | integer | yes | 1 to 20 |
| travel_type | string | yes | solo, couple, family, group |
| preferred_categories | list string | no | nature, culture, recreation, general |
| preferred_sub_categories | list string | no | known sub-categories |
| preferred_locations | list string | no | Bali regency or city names |
| top_k | integer | no | default 5, max 10 |

### Success Response

Status code: `200`

```json
{
  "status": "success",
  "input_summary": {
    "total_budget": 5000000,
    "duration_days": 3,
    "num_people": 2,
    "travel_type": "family",
    "preferred_categories": ["nature", "culture"],
    "preferred_sub_categories": ["beach", "temple"],
    "preferred_locations": ["Badung", "Gianyar"],
    "top_k": 5
  },
  "budget": {
    "tier": "medium",
    "budget_per_person_per_day": 833333,
    "total_budget": 5000000
  },
  "budget_allocation": {
    "items": [
      {
        "component": "destination_tickets",
        "amount": 1250000,
        "percentage": 25
      },
      {
        "component": "local_transport",
        "amount": 1250000,
        "percentage": 25
      },
      {
        "component": "food",
        "amount": 1500000,
        "percentage": 30
      },
      {
        "component": "buffer",
        "amount": 1000000,
        "percentage": 20
      }
    ],
    "total_allocated": 5000000,
    "is_within_budget": true
  },
  "recommended_destinations": [
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
      "maps_url": null,
      "image_url": null,
      "score": 0.92,
      "match_reasons": [
        "Matches preferred category",
        "Suitable for selected budget tier"
      ]
    }
  ],
  "summary": {
    "recommended_count": 1,
    "total_estimated_cost": 5000000,
    "remaining_budget": 0,
    "message": "Recommendation generated successfully."
  },
  "warnings": []
}
```

### Error Response Format

Use a consistent error format when custom validation is needed.

```json
{
  "status": "error",
  "message": "Invalid request payload",
  "errors": [
    {
      "field": "total_budget",
      "reason": "total_budget must be greater than 0"
    }
  ]
}
```

FastAPI default validation error is acceptable during MVP, but custom validation can be added later.

## Contract Rules

1. Do not remove existing response fields without updating this document, tests, and frontend.
2. Do not rename request fields without updating this document, tests, and frontend.
3. `budget_allocation.total_allocated` must not exceed `total_budget`.
4. `summary.remaining_budget` must be greater than or equal to 0.
5. Frontend must not implement business logic that belongs to backend services.
