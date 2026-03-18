"""
lib/questionnaires/qvt/questionnaire.py
Pipeline principal du questionnaire QVT.
"""

import re
import numpy as np
import pandas as pd

from lib.common import (
    BaseQuestionnaire, clean_pii, enrich_sociodem,
    clip_likert, compute_group_score, normalize_text,
)
from .config import (
    LIKERT_MIN, LIKERT_MAX, THRESHOLDS,
    RENAME_MAPPING, INVERT_ITEMS, DIMENSIONS,
)


ITEM_PATTERN = re.compile(
    r"Q\d+_(relations|contenu|environnement|organisation|developpement|equilibre)$"
)


def _fuzzy_rename(df: pd.DataFrame) -> pd.DataFrame:
    norm_map = {normalize_text(k): v for k, v in RENAME_MAPPING.items()}
    rename = {}
    for col in df.columns:
        nc = normalize_text(col)
        if nc in norm_map:
            rename[col] = norm_map[nc]
    return df.rename(columns=rename) if rename else df


class QVTQuestionnaire(BaseQuestionnaire):
    """Pipeline QVT — Qualité de Vie au Travail (ANACT)."""

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df, _ = clean_pii(df)
        df = enrich_sociodem(df)
        return df

    def score(self, df: pd.DataFrame) -> pd.DataFrame:
        df_out = df.copy()
        df_out = _fuzzy_rename(df_out)

        # Nettoyage Likert
        for col in [c for c in df_out.columns if ITEM_PATTERN.match(c)]:
            df_out[col] = clip_likert(df_out[col], LIKERT_MIN, LIKERT_MAX)

        # Scores par dimension
        for dim in DIMENSIONS:
            col_name = f"{dim}_score"
            computed = compute_group_score(df_out, dim, multiplier=1)
            if computed.notna().any():
                df_out[col_name] = computed
            elif col_name not in df_out.columns:
                df_out[col_name] = np.nan

        # Score global
        dim_cols = [f"{d}_score" for d in DIMENSIONS if f"{d}_score" in df_out.columns]
        if dim_cols:
            df_out["qvt_global_score"] = df_out[dim_cols].mean(axis=1, skipna=True)

        return df_out

    def classify(self, df: pd.DataFrame) -> pd.DataFrame:
        df_out = df.copy()
        for col, thresh in THRESHOLDS.items():
            if col in df_out.columns:
                max_possible = col.replace("_score", "")
                df_out[f"{col}_cat"] = np.where(
                    df_out[col].isna(), "Non renseigné",
                    np.where(df_out[col] < thresh * 0.6, "Insatisfaisant",
                             np.where(df_out[col] < thresh, "Mitigé", "Satisfaisant"))
                )
        return df_out

    def analytics(self, df: pd.DataFrame) -> dict:
        from .analytics import QVTAnalytics
        return QVTAnalytics(df).compute()

    def count_items(self, df: pd.DataFrame) -> int:
        return sum(1 for c in df.columns if ITEM_PATTERN.match(c))
