# Decision Log - BaliNavi

This document records technical decisions so the project remains consistent.

## 2026-05-20 - MVP Scope

Decision:
Build BaliNavi as an MVP focused on budget tier, destination recommendation, budget allocation, FastAPI backend, Streamlit frontend, Docker, and GitHub Actions.

Reason:
The project must remain realistic for capstone scope and avoid feature creep.

Impact:
Out-of-scope features such as authentication, database, dynamic pricing, detailed itinerary, hotel booking, flight recommendation, and production Kubernetes deployment are moved to backlog.

---

## 2026-05-20 - Backend Framework

Decision:
Use FastAPI for backend API.

Reason:
FastAPI provides request validation, automatic OpenAPI documentation, good testing support, and is lightweight enough for the MVP.

Impact:
Backend exposes `/health`, `/metadata`, and `/plan-trip`.

---

## 2026-05-20 - Frontend Framework

Decision:
Use Streamlit for frontend prototype.

Reason:
Streamlit is fast for building data-driven prototypes and matches the MVP requirement for a simple interactive app.

Impact:
Frontend should call backend API and should not duplicate business logic.

---

## 2026-05-20 - Recommender Approach

Decision:
Use Scikit-learn for content-based filtering.

Reason:
The MVP uses destination metadata such as category, tags, description, location, rating, and price. This can be handled effectively using TF-IDF and cosine similarity.

Impact:
TensorFlow is not used in MVP. TensorFlow may be considered later for personalized recommendation, image-based recommendation, neural collaborative filtering, or multi-modal recommendation.

---

## 2026-05-20 - Budget Allocation Approach

Decision:
Use rule-based budget allocation.

Reason:
The MVP needs explainable and controllable budget allocation. A rule-based approach is easier to validate and explain during demo.

Default components:

- destination_tickets,
- local_transport,
- food,
- buffer.

Rule:

```text
total_allocated <= total_budget
```

---

## 2026-05-20 - Containerization

Decision:
Use two Docker containers:

1. backend container for FastAPI,
2. frontend container for Streamlit.

Reason:
Separating frontend and backend keeps the architecture clear and closer to production practice.

Impact:
Use `docker-compose.yml` to run both services locally.

---

## 2026-05-20 - CI/CD

Decision:
Use GitHub Actions for automated tests and Docker build validation.

Reason:
This improves reproducibility and prevents broken code from being merged.

Workflow:

- install dependencies,
- run Pytest,
- build backend Docker image,
- build frontend Docker image,
- validate Docker Compose config.

---

## 2026-05-20 - Data Storage for MVP

Decision:
Use CSV files and local artifacts for MVP.

Reason:
A database is not required for the initial prototype.

Impact:
Use:

```text
data/raw/
data/processed/
data/final/
artifacts/
```

PostgreSQL or other databases can be added in a future production stage.

---

## 2026-05-20 - AGENTS.md Handling

Decision:
Do not upload `AGENTS.md` to the public GitHub repository for now.

Reason:
The team prefers to share it manually.

Impact:
When using Codex, the private AGENTS.md content must be provided manually in the prompt or shared directly with the team.
