# BaliNavi: Smart Travel Budgeting Platform

BaliNavi is a smart tourism MVP that helps tourists plan a Bali trip based on total budget, trip duration, number of people, travel type, and destination preferences.

The system returns:

- budget tier,
- destination recommendations,
- estimated budget allocation,
- simple visualization through Streamlit.

## Project Theme

AI for Smart Tourism Experience

## MVP Scope

The MVP focuses on:

- Bali destination dataset processing,
- content-based destination recommendation,
- budget tier classification,
- rule-based budget allocation,
- FastAPI backend,
- Streamlit frontend,
- Dockerized backend and frontend,
- GitHub Actions for tests and Docker image build.

Out-of-scope features are documented in `docs/MVP_SCOPE.md`.

## Technology Stack

| Area | Technology |
|---|---|
| Language | Python 3.12 |
| Data processing | Pandas, NumPy |
| Recommender | Scikit-learn |
| Artifact | Joblib |
| Backend | FastAPI, Uvicorn, Pydantic |
| Frontend | Streamlit, Requests |
| Visualization | Plotly, Matplotlib |
| Testing | Pytest, HTTPX |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Documentation | Markdown |

## Project Structure

See `PROJECT_STRUCTURE.md` for the full folder structure.

Main folders:

```text
docs/              project documentation and guardrails
app/backend/       FastAPI backend
app/frontend/      Streamlit frontend
src/               data, preprocessing, features, models, services
data/              raw, processed, and final datasets
artifacts/         model and vectorizer artifacts
notebooks/         EDA and experiments
tests/             automated tests
docker/            Dockerfiles
.github/           GitHub Actions and PR template
```

## API Endpoints

The MVP backend provides:

```text
GET  /health
GET  /metadata
POST /plan-trip
```

Detailed request and response format is documented in `docs/API_CONTRACT.md`.

## Local Setup

Create virtual environment:

```bash
python -m venv .venv
```

Activate virtual environment.

Windows:

```bash
.venv\Scripts\activate
```

Mac or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Backend Locally

```bash
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

## Run Frontend Locally

```bash
streamlit run app/frontend/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

## Run Tests

```bash
pytest tests/ -v
```

## Run with Docker Compose

```bash
docker compose up --build
```

Open:

```text
Backend API   : http://localhost:8000
API Docs      : http://localhost:8000/docs
Streamlit App : http://localhost:8501
```

## Branching Strategy

Recommended branches:

```text
main       stable demo version
develop    integration branch
feature/*  feature work branch
```

Examples:

```text
feature/backend-api
feature/frontend-streamlit
feature/data-preprocessing
feature/recommender-model
feature/budget-allocation
feature/docker-ci
```

## Documentation

### Dokumen Proyek

| File | Kegunaan |
|---|---|
| [`docs/PROJECT_PLAN_SUMMARY.md`](docs/PROJECT_PLAN_SUMMARY.md) | Ringkasan rencana proyek |
| [`docs/MVP_SCOPE.md`](docs/MVP_SCOPE.md) | Batasan scope dan definisi selesai |
| [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md) | Kontrak API backend dan frontend |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Arsitektur sistem dan tanggung jawab folder |
| [`docs/TASK_TEMPLATE.md`](docs/TASK_TEMPLATE.md) | Template task untuk tim dan Codex |
| [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md) | Riwayat keputusan teknis |

### Panduan Tim dan Workflow

| File | Kegunaan |
|---|---|
| [`docs/WORKFLOW.md`](docs/WORKFLOW.md) | Alur kerja tim dan aturan kolaborasi |
| [`docs/TEAM_ROLES.md`](docs/TEAM_ROLES.md) | Pembagian peran dan tanggung jawab |
| [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md) | Strategi branching dan alur Git |
| [`docs/DEVELOPMENT_GUIDE.md`](docs/DEVELOPMENT_GUIDE.md) | Panduan setup dan pengembangan lokal |
| [`docs/TESTING_GUIDE.md`](docs/TESTING_GUIDE.md) | Panduan testing dan menulis test |
| [`docs/DOCKER_GUIDE.md`](docs/DOCKER_GUIDE.md) | Panduan Docker dan Docker Compose |

### Panduan Area Teknis

| File | Kegunaan |
|---|---|
| [`docs/BACKEND_GUIDE.md`](docs/BACKEND_GUIDE.md) | Panduan FastAPI backend |
| [`docs/FRONTEND_GUIDE.md`](docs/FRONTEND_GUIDE.md) | Panduan Streamlit frontend |
| [`docs/DATA_PIPELINE_GUIDE.md`](docs/DATA_PIPELINE_GUIDE.md) | Panduan data pipeline |
| [`docs/RECOMMENDER_GUIDE.md`](docs/RECOMMENDER_GUIDE.md) | Panduan sistem rekomendasi |
| [`docs/BUDGET_ENGINE_GUIDE.md`](docs/BUDGET_ENGINE_GUIDE.md) | Panduan budget tier dan alokasi |
| [`docs/DEMO_GUIDE.md`](docs/DEMO_GUIDE.md) | Panduan persiapan dan menjalankan demo |

## Notes for Team

- Do not commit `.env`.
- Do not commit large raw datasets unless approved.
- Do not commit large model artifacts unless required for demo.
- Keep API contract stable.
- Keep business logic in `src/services/`.
- Keep Streamlit frontend focused on UI and API calls.
- Move out-of-scope ideas to backlog before implementation.
