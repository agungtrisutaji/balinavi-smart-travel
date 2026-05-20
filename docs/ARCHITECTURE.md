# Architecture - BaliNavi

## High-Level Architecture

```text
User
  |
  v
Streamlit Frontend
  |
  v
FastAPI Backend
  |
  v
Service Layer
  |-- budget_service
  |-- allocation_service
  |-- recommender_service
  |
  v
Data and Model Layer
  |-- dataset files
  |-- model artifacts
  |-- vectorizer artifacts
```

## Main Runtime Flow

1. User opens Streamlit frontend.
2. User fills trip form.
3. Streamlit sends request to `POST /plan-trip`.
4. FastAPI validates request with schema.
5. Backend calls budget tier service.
6. Backend calls allocation service.
7. Backend calls recommender service.
8. Backend returns recommendation and budget allocation.
9. Streamlit displays result and visualization.

## Folder Responsibilities

### `app/backend/`

FastAPI application.

Responsibilities:

- define API entrypoint,
- define routes,
- validate request and response schemas,
- call service layer,
- expose `/health`, `/metadata`, and `/plan-trip`.

### `app/frontend/`

Streamlit application.

Responsibilities:

- display input form,
- call backend API,
- show recommendation results,
- show budget allocation visualization,
- avoid business logic duplication.

### `src/services/`

Business logic layer.

Responsibilities:

- classify budget tier,
- allocate budget,
- return recommendations,
- keep API route handlers small.

### `src/models/`

Machine learning and recommender layer.

Responsibilities:

- train content-based recommender,
- save model or vectorizer artifacts,
- evaluate recommendation output,
- provide model logic that can be called by services.

### `src/preprocessing/`

Dataset preprocessing layer.

Responsibilities:

- clean raw dataset,
- handle duplicates,
- normalize categories,
- build quality flags,
- prepare processed dataset.

### `src/features/`

Feature engineering layer.

Responsibilities:

- build `content_text`,
- build normalized price or budget features,
- build popularity features,
- prepare model-ready dataset.

### `data/`

Dataset storage.

Recommended convention:

```text
data/raw/        original data files
data/processed/  cleaned intermediate files
data/final/      final model-ready files
```

Large or private datasets should not be committed unless the team explicitly approves.

### `artifacts/`

Model artifact storage.

Potential files:

```text
artifacts/vectorizer.pkl
artifacts/recommender.pkl
artifacts/metadata.json
```

Large artifacts should not be committed unless needed for demo and approved by the team.

### `tests/`

Automated tests.

Minimum tests:

- API contract tests,
- budget tier tests,
- allocation tests,
- recommender service tests.

### `docker/`

Docker build files.

Expected files:

```text
docker/backend.Dockerfile
docker/frontend.Dockerfile
```

### `.github/workflows/`

GitHub Actions CI workflow.

Expected workflow:

- install dependencies,
- run tests,
- build backend Docker image,
- build frontend Docker image,
- validate Docker Compose config.

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Data processing | Pandas, NumPy |
| Recommender | Scikit-learn |
| Artifact storage | Joblib |
| Backend | FastAPI, Uvicorn, Pydantic |
| Frontend | Streamlit, Requests |
| Visualization | Plotly, Matplotlib |
| Testing | Pytest, HTTPX |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Documentation | Markdown |

## Design Principles

1. Keep API contract stable.
2. Keep route handlers thin.
3. Keep business logic in services.
4. Keep preprocessing separate from runtime API logic.
5. Make dummy recommender replaceable by real model.
6. Avoid out-of-scope features in MVP.
7. Use environment variables for configurable runtime values.
8. Validate behavior with tests and CI.

## Future Production Extensions

Possible future additions:

- MLflow for experiment tracking,
- DVC for data and model versioning,
- PostgreSQL for persistent storage,
- Redis for caching,
- Prometheus and Grafana for monitoring,
- Evidently AI for drift monitoring,
- Airflow or Prefect for pipelines,
- Kubernetes for production orchestration.

These are not required for MVP.
