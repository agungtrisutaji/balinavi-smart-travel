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
| Language | Python 3.11 |
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

Important documents:

| File | Purpose |
|---|---|
| `docs/PROJECT_PLAN_SUMMARY.md` | Public-safe project plan summary |
| `docs/MVP_SCOPE.md` | Scope control and definition of done |
| `docs/API_CONTRACT.md` | Backend and frontend API contract |
| `docs/ARCHITECTURE.md` | System architecture and folder responsibility |
| `docs/TASK_TEMPLATE.md` | Task template for team and Codex |
| `docs/DECISION_LOG.md` | Technical decision history |

## Notes for Team

- Do not commit `.env`.
- Do not commit large raw datasets unless approved.
- Do not commit large model artifacts unless required for demo.
- Keep API contract stable.
- Keep business logic in `src/services/`.
- Keep Streamlit frontend focused on UI and API calls.
- Move out-of-scope ideas to backlog before implementation.
