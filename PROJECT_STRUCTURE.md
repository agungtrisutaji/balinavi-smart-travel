# Project Structure - BaliNavi

This document defines the recommended repository structure for BaliNavi MVP.

## Final Structure

```text
balinavi/
├── docs/
│   ├── PROJECT_PLAN_SUMMARY.md
│   ├── MVP_SCOPE.md
│   ├── API_CONTRACT.md
│   ├── ARCHITECTURE.md
│   ├── TASK_TEMPLATE.md
│   └── DECISION_LOG.md
│
├── app/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── trip_schema.py
│   │   └── core/
│   │       ├── __init__.py
│   │       └── config.py
│   │
│   └── frontend/
│       ├── __init__.py
│       └── streamlit_app.py
│
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── load_data.py
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   └── preprocess.py
│   ├── features/
│   │   ├── __init__.py
│   │   └── build_features.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train_recommender.py
│   │   ├── recommender.py
│   │   └── evaluate_recommender.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── budget_service.py
│   │   ├── allocation_service.py
│   │   └── recommender_service.py
│   └── utils/
│       ├── __init__.py
│       └── constants.py
│
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   ├── processed/
│   │   └── .gitkeep
│   └── final/
│       └── .gitkeep
│
├── artifacts/
│   └── .gitkeep
│
├── notebooks/
│   └── 01_eda_balinavi.ipynb
│
├── tests/
│   ├── __init__.py
│   ├── test_api_contract.py
│   ├── test_budget_rules.py
│   ├── test_allocation.py
│   └── test_recommender_service.py
│
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
│
├── .github/
│   ├── pull_request_template.md
│   └── workflows/
│       └── ci-docker.yml
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
├── README.md
└── PROJECT_STRUCTURE.md
```

## Folder Details

### `docs/`

Project documentation and guardrails.

This folder keeps the team aligned and prevents scope creep.

### `app/backend/`

FastAPI backend application.

Expected responsibilities:

- API entrypoint,
- route registration,
- request and response schema,
- configuration,
- backend service integration.

### `app/frontend/`

Streamlit frontend application.

Expected responsibilities:

- user input form,
- backend API call,
- recommendation display,
- budget allocation visualization.

### `src/data/`

Data loading utilities.

### `src/preprocessing/`

Dataset cleaning and preprocessing scripts.

### `src/features/`

Feature engineering scripts.

Examples:

- build content text,
- normalize category,
- compute popularity score,
- compute budget score.

### `src/models/`

Recommender model code.

Expected files:

- training script,
- recommender implementation,
- evaluation script.

### `src/services/`

Runtime business logic.

Expected services:

- budget tier service,
- budget allocation service,
- recommender service.

### `data/`

Dataset folders.

Recommended convention:

| Folder | Content |
|---|---|
| `data/raw/` | Original dataset files |
| `data/processed/` | Cleaned intermediate files |
| `data/final/` | Model-ready dataset |

### `artifacts/`

Model and vectorizer artifacts.

Potential files:

```text
vectorizer.pkl
recommender.pkl
metadata.json
```

### `notebooks/`

EDA and experiments.

Notebook code should be moved to scripts once it becomes part of the final pipeline.

### `tests/`

Automated tests.

Minimum test areas:

- API contract,
- budget tier,
- budget allocation,
- recommender service.

### `docker/`

Docker build files.

### `.github/`

GitHub collaboration and CI files.

## File Commit Policy

Commit these:

- source code,
- documentation,
- tests,
- requirements,
- Dockerfile,
- workflow files,
- `.env.example`,
- `.gitkeep` placeholder files.

Do not commit these unless approved:

- `.env`,
- virtual environment folders,
- large raw datasets,
- large model artifacts,
- credentials,
- API keys,
- tokens,
- logs.

## MVP Development Order

Recommended order:

1. Create repository structure.
2. Add docs and requirements.
3. Add FastAPI skeleton.
4. Add API schemas.
5. Add service skeletons.
6. Add tests.
7. Add Streamlit skeleton.
8. Add Dockerfiles and Docker Compose.
9. Add GitHub Actions.
10. Integrate dataset.
11. Implement recommender model.
12. Improve UI and visualization.
13. Finalize documentation and demo.
