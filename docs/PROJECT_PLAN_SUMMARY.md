# Project Plan Summary - BaliNavi

## Project Identity

Project name: BaliNavi: Smart Travel Budgeting Platform
Team ID: PJK-GM004
Theme: AI for Smart Tourism Experience

BaliNavi is an MVP smart tourism application designed to help tourists plan a trip to Bali based on budget, duration, number of people, travel type, and destination preferences.

This file is a public-safe project summary. It intentionally avoids participant ID numbers and sensitive personal information.

## Problem Statement

Tourists often struggle to plan a Bali trip because destination information, estimated costs, ratings, and travel recommendations are scattered across many platforms. This makes it difficult to compare destinations, estimate total travel costs, and make decisions that match their budget and preferences.

BaliNavi aims to reduce this friction by providing a simple budgeting and recommendation platform.

## Target Users

- Independent travelers
- First-time visitors to Bali
- Budget-sensitive travelers
- Mobile-first travelers
- Families or groups planning a trip together

## MVP Goal

Build an end-to-end prototype that accepts user trip preferences and returns:

1. budget tier,
2. recommended Bali destinations,
3. estimated budget allocation,
4. simple visualization through Streamlit.

## Main User Input

The MVP should accept:

- total budget,
- trip duration in days,
- number of people,
- travel type,
- preferred categories,
- preferred sub-categories,
- preferred locations,
- number of recommendations requested.

## Main System Output

The MVP should return:

- budget tier: low, medium, or high,
- budget per person per day,
- budget allocation by component,
- destination recommendations,
- ticket estimate per destination,
- recommendation score,
- explanation or match reasons,
- summary and warnings.

## Project Scope

The project focuses on:

- Bali destination dataset preparation,
- data cleaning and preprocessing,
- feature engineering,
- content-based destination recommendation,
- rule-based budget tier classification,
- rule-based budget allocation,
- FastAPI backend,
- Streamlit frontend,
- Dockerized backend and frontend,
- GitHub Actions for test and Docker build validation,
- technical documentation and demo.

## Out of Scope for MVP

The MVP does not include:

- flight recommendation,
- hotel booking,
- culinary recommendation,
- dynamic pricing,
- detailed day-by-day itinerary generation,
- user authentication,
- payment system,
- database persistence,
- production-grade Kubernetes deployment,
- paid external API integration.

## Suggested Team Responsibility Map

| Area | Responsibility |
|---|---|
| Backend and integration | FastAPI, API contract, service integration, Docker, CI |
| Frontend | Streamlit UI, input form, result page, visualization |
| Data engineering | Dataset collection, cleaning, preprocessing, EDA |
| AI systems and budget logic | Feature engineering, budget rules, allocation engine |
| Recommender model | Content-based filtering, tuning, evaluation |

## Technical Approach

The recommended MVP approach is:

1. Use a Bali destination dataset as the base data source.
2. Clean and normalize destination attributes.
3. Build content text from name, category, tags, activity, description, and location.
4. Use Scikit-learn TF-IDF and cosine similarity for content-based recommendation.
5. Classify user budget into low, medium, or high tier.
6. Allocate budget into destination tickets, local transport, food, and buffer.
7. Serve the logic through FastAPI.
8. Display the result through Streamlit.
9. Validate the project with Pytest, Docker, and GitHub Actions.

## Milestone Summary

| Phase | Focus | Output |
|---|---|---|
| Phase 1 | Repository setup and data preparation | Repo structure, data schema, initial docs |
| Phase 2 | Cleaning, preprocessing, and EDA | Clean dataset, EDA notebook, feature plan |
| Phase 3 | Recommender and budget logic | Model baseline, budget tier rules, allocation engine |
| Phase 4 | Backend, frontend, and Docker integration | End-to-end prototype |
| Phase 5 | Testing, documentation, and demo | Final MVP, test result, demo script |

## Key Risks

| Risk | Mitigation |
|---|---|
| Dataset is incomplete or inconsistent | Use minimum required fields, manual curation, quality flags |
| Project scope becomes too large | Keep MVP scope fixed and move extra features to backlog |
| Recommendation quality is weak | Use content-based filtering, budget filter, and scenario testing |
| Budget allocation is unrealistic | Use clear constraints and ensure allocation never exceeds total budget |
| Integration is delayed | Start with dummy recommender and integrate incrementally |
| Deployment fails during demo | Prepare local Docker demo and manual run instructions |

## Current MVP Maturity Target

BaliNavi targets:

MLOps Level 2 with partial Level 3 practice.

This means:

- structured repository,
- reproducible data and model workflow,
- backend API,
- Streamlit frontend,
- Dockerized services,
- automated tests,
- GitHub Actions for test and Docker build validation.
