# MVP Scope - BaliNavi

## MVP Objective

Build a working end-to-end Bali trip budgeting and recommendation prototype.

The MVP must help users answer:

Given my budget, trip duration, group size, travel type, and destination preference, which Bali destinations are suitable and how should my budget be allocated?

## In Scope

The MVP includes:

1. Destination dataset preparation.
2. Dataset cleaning and preprocessing.
3. Feature engineering for destination recommendation.
4. Content-based recommendation using destination metadata.
5. Budget tier classification.
6. Rule-based budget allocation.
7. FastAPI backend.
8. Streamlit frontend.
9. Dockerized backend and frontend.
10. GitHub Actions for tests and Docker image build.
11. Basic documentation and demo guide.

## Core MVP Features

### 1. Budget Tier Classification

Input:

- total budget,
- duration days,
- number of people.

Output:

- low,
- medium,
- high.

Default formula:

```text
budget_per_person_per_day = total_budget / duration_days / num_people
```

Default tier rule:

| Tier | Rule |
|---|---|
| low | below 500000 IDR per person per day |
| medium | 500000 to 1000000 IDR per person per day |
| high | above 1000000 IDR per person per day |

### 2. Budget Allocation

The MVP allocates total budget into:

- destination_tickets,
- local_transport,
- food,
- buffer.

Rule:

```text
total_allocated must be less than or equal to total_budget
```

### 3. Destination Recommendation

The MVP uses destination metadata such as:

- name,
- category,
- sub-category,
- tags,
- activity,
- description,
- location,
- rating,
- ticket price.

The baseline approach is:

```text
content text -> TF-IDF -> cosine similarity -> budget filter -> ranked recommendations
```

### 4. Streamlit UI

The UI must provide:

- input form,
- recommendation result,
- budget tier result,
- budget allocation visualization,
- destination table or cards.

## Out of Scope

Do not implement these features in the MVP unless approved by the team:

- user login,
- user profile,
- database persistence,
- flight recommendation,
- hotel booking,
- culinary recommendation,
- payment system,
- dynamic pricing,
- detailed day-by-day itinerary,
- route optimization,
- Google Maps paid API integration,
- production Kubernetes deployment,
- advanced personalization based on user history.

## Backlog Candidates

These can be considered after MVP is stable:

- MLflow experiment tracking,
- DVC data versioning,
- PostgreSQL database,
- Redis caching,
- Prometheus and Grafana monitoring,
- Evidently AI for data drift monitoring,
- user feedback loop,
- cloud deployment,
- TensorFlow-based personalized recommendation.

## Definition of Done

The MVP is considered done when:

- `GET /health` works,
- `GET /metadata` works,
- `POST /plan-trip` works,
- Streamlit can call FastAPI backend,
- recommendation result is displayed,
- budget allocation does not exceed total budget,
- Docker Compose runs backend and frontend,
- Pytest tests pass,
- GitHub Actions passes,
- README explains how to run the project,
- project documentation is updated.

## Scope Control Rule

If a requested feature is not listed in the In Scope section, it must be added to backlog first and discussed by the team before implementation.
