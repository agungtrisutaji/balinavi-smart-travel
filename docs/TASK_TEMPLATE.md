# Codex and Team Task Template

Use this template when assigning work to Codex or team members.

## Task Title

[Short and specific title]

## Context

This task is part of BaliNavi MVP.

Before working, read:

- `docs/PROJECT_PLAN_SUMMARY.md`
- `docs/MVP_SCOPE.md`
- `docs/API_CONTRACT.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISION_LOG.md`

## Goal

[Describe one specific goal only.]

Example:

Implement budget tier classification service.

## Files Allowed to Change

- [file or folder 1]
- [file or folder 2]

Do not modify files outside this list unless necessary. If necessary, explain why.

## Requirements

- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

## Out of Scope

- [What not to implement]
- [What not to change]

Example:

- Do not add database integration.
- Do not add authentication.
- Do not change API contract.

## Acceptance Criteria

- [ ] Feature works as requested.
- [ ] Tests are added or updated.
- [ ] Existing tests pass.
- [ ] No unrelated files are modified.
- [ ] Documentation is updated if behavior changes.

## Tests to Run

```bash
pytest tests/ -v
```

If Docker files are changed:

```bash
docker compose config
docker compose build
```

## Expected Final Report

At the end of the task, report:

1. Summary of changes
2. Files changed
3. Tests run
4. Assumptions
5. Follow-up needed

## Example Task Prompt

```text
You are working on BaliNavi MVP.

Task:
Implement rule-based budget allocation.

Read:
- docs/MVP_SCOPE.md
- docs/API_CONTRACT.md
- docs/ARCHITECTURE.md

Allowed files:
- src/services/allocation_service.py
- tests/test_allocation.py

Requirements:
- Allocate total budget into destination_tickets, local_transport, food, and buffer.
- Total allocation must not exceed total_budget.
- Return items, total_allocated, and is_within_budget.

Out of scope:
- Do not implement itinerary.
- Do not add database.
- Do not change API contract.

Run:
pytest tests/ -v

Report summary, files changed, tests run, assumptions, and follow-up.
```
