"""
Training script for BaliNavi content-based recommender.

Usage (CLI):
    python -m src.models.train_recommender
    python -m src.models.train_recommender --data-path data/clustered/bali_destination.csv --output-dir artifacts/

Usage (Python):
    from src.models.train_recommender import train_recommender
    result = train_recommender()
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from src.models.recommender import RUNTIME_COLUMNS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default paths & TF-IDF hyper-parameters
# ---------------------------------------------------------------------------
DEFAULT_DATA_PATH = "data/clustered/bali_destination.csv"
DEFAULT_OUTPUT_DIR = "artifacts"

DEFAULT_TFIDF_PARAMS: dict = {
    "max_features": 5_000,
    "ngram_range": (1, 2),
    "min_df": 2,
    "max_df": 0.90,
    "sublinear_tf": True,
}


# ---------------------------------------------------------------------------
# Training function
# ---------------------------------------------------------------------------
def train_recommender(
    data_path: str = DEFAULT_DATA_PATH,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    *,
    max_features: int = DEFAULT_TFIDF_PARAMS["max_features"],
    ngram_range: tuple[int, int] = DEFAULT_TFIDF_PARAMS["ngram_range"],
    min_df: int = DEFAULT_TFIDF_PARAMS["min_df"],
    max_df: float = DEFAULT_TFIDF_PARAMS["max_df"],
    sublinear_tf: bool = DEFAULT_TFIDF_PARAMS["sublinear_tf"],
) -> dict:
    """Train the TF-IDF recommender and persist artifacts.

    Returns a status dict with training metadata.
    """
    logger.info("Loading dataset from %s …", data_path)
    df = pd.read_csv(data_path)
    total_rows = len(df)

    # --- 1. Filter eligible destinations --------------------------------
    if "recommendation_eligible" in df.columns:
        df = df[df["recommendation_eligible"] == True].copy()  # noqa: E712
    eligible_rows = len(df)
    logger.info("Eligible destinations: %d / %d", eligible_rows, total_rows)

    if eligible_rows == 0:
        raise ValueError("No eligible destinations found in dataset.")

    # --- 2. Enrich content_text with cluster_label ----------------------
    if "cluster_label" in df.columns:
        df["content_text"] = (
            df["content_text"].fillna("").astype(str)
            + " "
            + df["cluster_label"].fillna("").astype(str).str.lower()
        )
        logger.info("Enriched content_text with cluster_label.")
    else:
        logger.warning("Column 'cluster_label' not found; using content_text as-is.")

    # Clean up whitespace
    df["content_text"] = df["content_text"].str.strip().str.replace(r"\s+", " ", regex=True)

    # --- 3. Fit TF-IDF Vectorizer ----------------------------------------
    tfidf_params = {
        "max_features": max_features,
        "ngram_range": ngram_range,
        "min_df": min_df,
        "max_df": max_df,
        "sublinear_tf": sublinear_tf,
    }
    logger.info("Fitting TfidfVectorizer with params: %s", tfidf_params)

    vectorizer = TfidfVectorizer(**tfidf_params)
    tfidf_matrix = vectorizer.fit_transform(df["content_text"])
    logger.info("TF-IDF matrix shape: %s", tfidf_matrix.shape)

    # --- 4. Prepare destination data for runtime ------------------------
    # Keep only columns needed at inference time
    available_runtime_cols = [c for c in RUNTIME_COLUMNS if c in df.columns]
    destination_data = df[available_runtime_cols].reset_index(drop=True)

    # --- 5. Persist artifacts -------------------------------------------
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    joblib.dump(vectorizer, out / "vectorizer.pkl")
    joblib.dump(tfidf_matrix, out / "tfidf_matrix.pkl")
    joblib.dump(destination_data, out / "destination_data.pkl")

    metadata = {
        "status": "trained",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "data_path": str(data_path),
        "total_rows": total_rows,
        "eligible_rows": eligible_rows,
        "tfidf_shape": list(tfidf_matrix.shape),
        "tfidf_params": {
            **tfidf_params,
            "ngram_range": list(tfidf_params["ngram_range"]),
        },
        "vocabulary_size": len(vectorizer.vocabulary_),
        "artifacts": [
            "vectorizer.pkl",
            "tfidf_matrix.pkl",
            "destination_data.pkl",
            "metadata.json",
        ],
    }
    with open(out / "metadata.json", "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2, ensure_ascii=False)

    logger.info("Artifacts saved to %s/", out)
    logger.info("Training complete ✓")
    return metadata


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------
def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train BaliNavi content-based recommender.",
    )
    parser.add_argument(
        "--data-path",
        default=DEFAULT_DATA_PATH,
        help=f"Path to CSV dataset (default: {DEFAULT_DATA_PATH})",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for saved artifacts (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument("--max-features", type=int, default=DEFAULT_TFIDF_PARAMS["max_features"])
    parser.add_argument("--min-df", type=int, default=DEFAULT_TFIDF_PARAMS["min_df"])
    parser.add_argument("--max-df", type=float, default=DEFAULT_TFIDF_PARAMS["max_df"])
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = _parse_args()
    result = train_recommender(
        data_path=args.data_path,
        output_dir=args.output_dir,
        max_features=args.max_features,
        min_df=args.min_df,
        max_df=args.max_df,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
