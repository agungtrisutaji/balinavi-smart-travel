"""
Recommender model classes for BaliNavi.

- DummyRecommender: placeholder (backward compatibility).
- ContentBasedRecommender: TF-IDF + cosine similarity + hybrid scoring.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scoring weights (sum = 1.0 before budget penalty)
# ---------------------------------------------------------------------------
W_COSINE = 0.60
W_CATEGORY = 0.15
W_LOCATION = 0.10
W_POPULARITY = 0.10
W_SUB_CATEGORY = 0.05
BUDGET_PENALTY = -0.30

# Columns persisted in destination_data artifact
RUNTIME_COLUMNS = [
    "destination_id",
    "name",
    "category_main",
    "sub_category",
    "district",
    "regency_city",
    "estimated_ticket_price",
    "rating",
    "review_count",
    "popularity_score",
    "latitude",
    "longitude",
    "maps_url",
    "image_url",
    "budget_tiers",
    "content_text",
]


# ---------------------------------------------------------------------------
# DummyRecommender — kept for backward compatibility / fallback
# ---------------------------------------------------------------------------
class DummyRecommender:
    def recommend(self, destinations: list[dict], top_k: int = 5) -> list[dict]:
        return destinations[:top_k]


# ---------------------------------------------------------------------------
# ContentBasedRecommender
# ---------------------------------------------------------------------------
class ContentBasedRecommender:
    """Content-based recommender using TF-IDF + cosine similarity + hybrid scoring."""

    def __init__(
        self,
        vectorizer,
        tfidf_matrix,
        destination_data: pd.DataFrame,
        metadata: dict | None = None,
    ):
        self.vectorizer = vectorizer
        self.tfidf_matrix = tfidf_matrix
        self.destination_data = destination_data.reset_index(drop=True)
        self.metadata = metadata or {}

    # ------------------------------------------------------------------
    # Factory – load from artifacts directory
    # ------------------------------------------------------------------
    @classmethod
    def load(cls, artifacts_dir: str = "artifacts") -> "ContentBasedRecommender":
        """Load all artifacts from *artifacts_dir* and return a ready instance."""
        base = Path(artifacts_dir)

        vectorizer = joblib.load(base / "vectorizer.pkl")
        tfidf_matrix = joblib.load(base / "tfidf_matrix.pkl")
        destination_data: pd.DataFrame = joblib.load(base / "destination_data.pkl")

        metadata: dict = {}
        metadata_path = base / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, encoding="utf-8") as fh:
                metadata = json.load(fh)

        logger.info(
            "Loaded ContentBasedRecommender – %d destinations, metadata=%s",
            len(destination_data),
            metadata.get("trained_at", "unknown"),
        )
        return cls(vectorizer, tfidf_matrix, destination_data, metadata)

    # ------------------------------------------------------------------
    # Core recommendation
    # ------------------------------------------------------------------
    def recommend(
        self,
        budget_tier: str,
        preferred_categories: list[str] | None = None,
        preferred_sub_categories: list[str] | None = None,
        preferred_locations: list[str] | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        """Generate top-K recommendations with hybrid scoring."""

        categories = set(preferred_categories or [])
        sub_categories = set(preferred_sub_categories or [])
        locations = set(preferred_locations or [])

        # --- 1. Build query text from user preferences -----------------
        query_parts: list[str] = []
        query_parts.extend(categories)
        query_parts.extend(sub_categories)
        query_parts.extend(locations)
        query_text = " ".join(query_parts).lower().strip()

        # If no preferences at all, use a generic query that captures
        # all categories so cosine similarity is spread evenly.
        if not query_text:
            query_text = "wisata bali destinasi"

        # --- 2. Cosine similarity (on-the-fly) -------------------------
        query_vec = self.vectorizer.transform([query_text])
        cos_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # --- 3. Hybrid scoring -----------------------------------------
        df = self.destination_data
        n = len(df)
        scores = np.zeros(n, dtype=np.float64)

        for i in range(n):
            row = df.iloc[i]

            # Cosine component
            cosine_val = float(cos_scores[i])

            # Category match
            cat_match = 1.0 if (categories and row["category_main"] in categories) else 0.0

            # Sub-category match
            subcat_match = (
                1.0 if (sub_categories and row["sub_category"] in sub_categories) else 0.0
            )

            # Location match
            loc_match = 1.0 if (locations and row["regency_city"] in locations) else 0.0

            # Popularity (already 0–1)
            pop = float(row.get("popularity_score", 0.0))

            # Budget penalty
            dest_tiers = str(row.get("budget_tiers", "")).split(",")
            budget_ok = budget_tier in dest_tiers
            penalty = 0.0 if budget_ok else BUDGET_PENALTY

            score = (
                W_COSINE * cosine_val
                + W_CATEGORY * cat_match
                + W_SUB_CATEGORY * subcat_match
                + W_LOCATION * loc_match
                + W_POPULARITY * pop
                + penalty
            )
            scores[i] = max(score, 0.0)  # clamp to non-negative

        # --- 4. Sort descending, pick top-K ----------------------------
        ranked_indices = np.argsort(-scores)[:top_k]

        results: list[dict] = []
        for idx in ranked_indices:
            idx = int(idx)
            if scores[idx] <= 0.0:
                continue  # skip zero-score entries
            row = df.iloc[idx]
            result = self._format_destination(row, scores[idx], cos_scores[idx], budget_tier, categories, sub_categories, locations)
            results.append(result)

        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _format_destination(
        row: pd.Series,
        final_score: float,
        cosine_score: float,
        budget_tier: str,
        categories: set[str],
        sub_categories: set[str],
        locations: set[str],
    ) -> dict:
        """Build a single destination dict conforming to API contract."""

        # Build dynamic match_reasons
        match_reasons: list[str] = []

        cos_pct = round(cosine_score * 100)
        match_reasons.append(f"Content similarity: {cos_pct}%")

        if categories and row["category_main"] in categories:
            match_reasons.append(f"Matches preferred category: {row['category_main']}")

        if sub_categories and row["sub_category"] in sub_categories:
            match_reasons.append(f"Matches preferred sub-category: {row['sub_category']}")

        if locations and row["regency_city"] in locations:
            match_reasons.append(f"Matches preferred location: {row['regency_city']}")

        dest_tiers = str(row.get("budget_tiers", "")).split(",")
        if budget_tier in dest_tiers:
            match_reasons.append(f"Suitable for {budget_tier} budget tier")
        else:
            match_reasons.append("Budget tier mismatch (penalty applied)")

        return {
            "destination_id": row["destination_id"],
            "name": row["name"],
            "category": row["category_main"],
            "sub_category": row["sub_category"],
            "district": row["district"],
            "regency_city": row["regency_city"],
            "estimated_ticket_price": int(row["estimated_ticket_price"]),
            "estimated_ticket_total": int(row["estimated_ticket_price"]),
            "rating": float(row["rating"]),
            "review_count": int(row["review_count"]),
            "popularity_score": round(float(row.get("popularity_score", 0.0)), 4),
            "latitude": float(row["latitude"]) if pd.notna(row.get("latitude")) else None,
            "longitude": float(row["longitude"]) if pd.notna(row.get("longitude")) else None,
            "maps_url": row.get("maps_url") if pd.notna(row.get("maps_url")) else None,
            "image_url": row.get("image_url") if pd.notna(row.get("image_url")) else None,
            "score": round(float(final_score), 4),
            "match_reasons": match_reasons,
        }
