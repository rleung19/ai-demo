"""
Build a new-user fallback list for the recommender from ADS operator results.

The ADS Recommender Operator may write a report with recommendations for new users
(e.g. in results/new_user_recommendations.csv or report.html). This helper:
1) Tries to load from common new-user CSVs in results_dir
2) If none found, builds a "popular items" list from recommendations.csv
3) Saves new_user_fallback.pkl (list of (product_id, score)) to artifact_dir

score.py can then use this when user_id is not in the main model.
"""

from __future__ import annotations

import os
from typing import List, Tuple, Optional

import joblib
import pandas as pd


def _infer_item_col(df: pd.DataFrame) -> Optional[str]:
    for c in ("PRODUCT_ID", "product_id", "item_id", "item", "movie_id", "ITEM_ID"):
        if c in df.columns:
            return c
    return None


def _infer_score_col(df: pd.DataFrame) -> Optional[str]:
    for c in ("RATING", "rating", "score", "Score", "SCORE"):
        if c in df.columns:
            return c
    return None


def build_and_save_new_user_fallback(
    results_dir: str,
    artifact_dir: str,
    recommendations_df: Optional[pd.DataFrame] = None,
    *,
    item_col: Optional[str] = None,
    score_col: Optional[str] = None,
    new_user_csv_path: Optional[str] = None,
    top_n: int = 200,
) -> List[Tuple[str, float]]:
    """
    Build a new-user fallback list and save to artifact_dir/new_user_fallback.pkl.

    Args:
        results_dir: Where the ADS operator wrote results (e.g. /home/datascience/results).
        artifact_dir: Where to save new_user_fallback.pkl (e.g. recommender_model_artifact).
        recommendations_df: DataFrame from recommendations.csv; used for popularity fallback
            if no dedicated new-user file is found.
        item_col: Name of item/product column. If None, inferred.
        score_col: Name of score/rating column. If None, inferred.
        new_user_csv_path: If set, use this CSV first (overrides results_dir search).
            Example: "/home/datascience/results/new_user_recommendations.csv"
        top_n: Max number of items in the fallback list.

    Returns:
        The fallback list of (product_id, score) used for new users.
    """
    fallback: List[Tuple[str, float]] = []

    # 1) Explicit path from operator report
    if new_user_csv_path and os.path.isfile(new_user_csv_path):
        try:
            df = pd.read_csv(new_user_csv_path)
            ic = item_col or _infer_item_col(df)
            sc = score_col or _infer_score_col(df)
            if ic and sc:
                tmp = df[[ic, sc]].drop_duplicates()
                tmp = tmp.sort_values(sc, ascending=False).head(top_n)
                fallback = [(str(row[ic]), float(row[sc])) for _, row in tmp.iterrows()]
                return _save_and_return(artifact_dir, fallback)
        except Exception:
            pass

    # 2) Search common filenames in results_dir
    candidates = (
        "new_user_recommendations.csv",
        "cold_start_recommendations.csv",
        "recommendations_new_users.csv",
        "new_users.csv",
    )
    for fn in candidates:
        p = os.path.join(results_dir, fn)
        if os.path.isfile(p):
            try:
                df = pd.read_csv(p)
                ic = item_col or _infer_item_col(df)
                sc = score_col or _infer_score_col(df)
                if ic and sc:
                    # Handle (user_id, item_id, score) by aggregating by item
                    if "user_id" in df.columns or "USER_ID" in df.columns:
                        agg = df.groupby(ic)[sc].mean().sort_values(ascending=False).head(top_n)
                        fallback = [(str(k), float(v)) for k, v in agg.items()]
                    else:
                        tmp = df[[ic, sc]].drop_duplicates()
                        tmp = tmp.sort_values(sc, ascending=False).head(top_n)
                        fallback = [(str(row[ic]), float(row[sc])) for _, row in tmp.iterrows()]
                    return _save_and_return(artifact_dir, fallback)
            except Exception:
                continue

    # 3) Popularity fallback from recommendations.csv
    if recommendations_df is not None and len(recommendations_df) > 0:
        ic = item_col or _infer_item_col(recommendations_df)
        sc = score_col or _infer_score_col(recommendations_df)
        if ic and sc:
            agg = (
                recommendations_df.groupby(ic)[sc]
                .mean()
                .sort_values(ascending=False)
                .head(top_n)
            )
            fallback = [(str(k), float(v)) for k, v in agg.items()]
            return _save_and_return(artifact_dir, fallback)

    return _save_and_return(artifact_dir, fallback)


def _save_and_return(artifact_dir: str, fallback: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
    os.makedirs(artifact_dir, exist_ok=True)
    joblib.dump(fallback, os.path.join(artifact_dir, "new_user_fallback.pkl"))
    return fallback
