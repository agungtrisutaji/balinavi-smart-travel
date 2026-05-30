"""
Evaluation module for BaliNavi content-based recommender.

Evaluates the recommender output using three metrics:
  1. Precision@K  – relevance of recommendations to user preferences.
  2. Category Coverage – diversity across requested categories.
  3. Budget Compliance Rate – alignment with user budget tier.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default test scenarios
# ---------------------------------------------------------------------------
DEFAULT_TEST_SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "Nature lover low budget",
        "budget_tier": "low",
        "preferred_categories": ["nature"],
        "preferred_sub_categories": ["beach", "waterfall"],
        "preferred_locations": ["Badung", "Gianyar"],
        "top_k": 5,
    },
    {
        "name": "Culture explorer medium budget",
        "budget_tier": "medium",
        "preferred_categories": ["culture"],
        "preferred_sub_categories": ["temple", "museum"],
        "preferred_locations": ["Gianyar"],
        "top_k": 5,
    },
    {
        "name": "Mixed preferences high budget",
        "budget_tier": "high",
        "preferred_categories": ["nature", "culture", "recreation"],
        "preferred_sub_categories": [],
        "preferred_locations": [],
        "top_k": 5,
    },
    {
        "name": "No preference medium budget",
        "budget_tier": "medium",
        "preferred_categories": [],
        "preferred_sub_categories": [],
        "preferred_locations": [],
        "top_k": 5,
    },
    {
        "name": "Recreation in Badung",
        "budget_tier": "low",
        "preferred_categories": ["recreation"],
        "preferred_sub_categories": ["landmark", "waterpark"],
        "preferred_locations": ["Badung"],
        "top_k": 5,
    },
]


# ---------------------------------------------------------------------------
# Metric functions
# ---------------------------------------------------------------------------
def precision_at_k(
    recommendations: list[dict],
    preferred_categories: list[str],
    preferred_sub_categories: list[str],
    preferred_locations: list[str],
) -> float:
    """Compute Precision@K.

    A recommendation is *relevant* if it matches at least one user
    preference (category, sub-category, or location).
    """
    if not recommendations:
        return 0.0

    relevant = 0
    cats = set(preferred_categories or [])
    subcats = set(preferred_sub_categories or [])
    locs = set(preferred_locations or [])

    for rec in recommendations:
        is_relevant = False
        if cats and rec.get("category") in cats:
            is_relevant = True
        if subcats and rec.get("sub_category") in subcats:
            is_relevant = True
        if locs and rec.get("regency_city") in locs:
            is_relevant = True
        # If no preferences specified, all recs are considered relevant
        if not cats and not subcats and not locs:
            is_relevant = True
        if is_relevant:
            relevant += 1

    return relevant / len(recommendations)


def category_coverage(
    recommendations: list[dict],
    preferred_categories: list[str],
) -> float:
    """Compute Category Coverage.

    Ratio of unique categories in recommendations to number of requested
    categories.  Returns 1.0 if no categories were requested.
    """
    if not preferred_categories:
        return 1.0
    if not recommendations:
        return 0.0

    requested = set(preferred_categories)
    found = {rec.get("category") for rec in recommendations} & requested
    return len(found) / len(requested)


def budget_compliance_rate(
    recommendations: list[dict],
    budget_tier: str,
) -> float:
    """Compute Budget Compliance Rate.

    Fraction of recommendations whose match_reasons indicate budget
    compliance (i.e. do NOT contain a penalty notice).
    """
    if not recommendations:
        return 0.0

    compliant = 0
    for rec in recommendations:
        reasons = rec.get("match_reasons", [])
        # Check for budget compliance in match reasons
        has_penalty = any("mismatch" in r.lower() or "penalty" in r.lower() for r in reasons)
        if not has_penalty:
            compliant += 1

    return compliant / len(recommendations)


# ---------------------------------------------------------------------------
# Main evaluation driver
# ---------------------------------------------------------------------------
def evaluate_recommender(
    recommender,
    test_scenarios: list[dict[str, Any]] | None = None,
    k: int = 5,
) -> dict[str, Any]:
    """Run evaluation scenarios against *recommender* and return metrics.

    Parameters
    ----------
    recommender : ContentBasedRecommender
        An already-loaded recommender instance.
    test_scenarios : list of dicts, optional
        Each dict must have: budget_tier, preferred_categories,
        preferred_sub_categories, preferred_locations.
        Defaults to ``DEFAULT_TEST_SCENARIOS``.
    k : int
        Number of recommendations per scenario.

    Returns
    -------
    dict with ``scenarios`` (per-scenario detail) and ``summary`` averages.
    """
    if test_scenarios is None:
        test_scenarios = DEFAULT_TEST_SCENARIOS

    scenario_results: list[dict[str, Any]] = []

    for scenario in test_scenarios:
        name = scenario.get("name", "unnamed")
        top_k = scenario.get("top_k", k)

        recs = recommender.recommend(
            budget_tier=scenario["budget_tier"],
            preferred_categories=scenario.get("preferred_categories"),
            preferred_sub_categories=scenario.get("preferred_sub_categories"),
            preferred_locations=scenario.get("preferred_locations"),
            top_k=top_k,
        )

        p_at_k = precision_at_k(
            recs,
            scenario.get("preferred_categories", []),
            scenario.get("preferred_sub_categories", []),
            scenario.get("preferred_locations", []),
        )
        cat_cov = category_coverage(recs, scenario.get("preferred_categories", []))
        budget_cr = budget_compliance_rate(recs, scenario["budget_tier"])

        result = {
            "scenario": name,
            "num_recommendations": len(recs),
            "precision_at_k": round(p_at_k, 4),
            "category_coverage": round(cat_cov, 4),
            "budget_compliance_rate": round(budget_cr, 4),
        }
        scenario_results.append(result)
        logger.info("  %s → P@K=%.2f  CatCov=%.2f  BudgetCR=%.2f", name, p_at_k, cat_cov, budget_cr)

    # --- Summary (averages) --------------------------------------------
    avg_precision = sum(s["precision_at_k"] for s in scenario_results) / len(scenario_results)
    avg_coverage = sum(s["category_coverage"] for s in scenario_results) / len(scenario_results)
    avg_budget = sum(s["budget_compliance_rate"] for s in scenario_results) / len(scenario_results)

    summary = {
        "avg_precision_at_k": round(avg_precision, 4),
        "avg_category_coverage": round(avg_coverage, 4),
        "avg_budget_compliance_rate": round(avg_budget, 4),
        "num_scenarios": len(scenario_results),
    }

    logger.info("Summary: %s", summary)

    return {
        "scenarios": scenario_results,
        "summary": summary,
    }
