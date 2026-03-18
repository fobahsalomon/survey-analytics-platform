"""
lib/questionnaires/mbi/questionnaire.py
Pipeline principal du Maslach Burnout Inventory (MBI-GS).
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
    RENAME_MAPPING, DIMENSIONS,
)


ITEM_PATTERN = re.compile(r"Q\d+_(exhaustion|cynicism|efficacy)$")


def _fuzzy_rename(df: pd.DataFrame) -> pd.DataFrame:
    """Renomme les colonnes source vers les codes internes MBI via matching normalisé."""
    norm_map = {normalize_text(k): v for k, v in RENAME_MAPPING.items()}
    rename = {}
    for col in df.columns:
        nc = normalize_text(col)
        if nc in norm_map:
            rename[col] = norm_map[nc]
    return df.rename(columns=rename) if rename else df


class MBIQuestionnaire(BaseQuestionnaire):
    """Pipeline Maslach Burnout Inventory — General Survey (MBI-GS)."""

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        # Nettoyage et enrichissement communs avant scoring MBI.
        df, _ = clean_pii(df)
        df = enrich_sociodem(df)
        return df

    def score(self, df: pd.DataFrame) -> pd.DataFrame:
        df_out = df.copy()
        df_out = _fuzzy_rename(df_out)

        # Mise au propre des réponses individuelles sur l'échelle MBI.
        for col in [c for c in df_out.columns if ITEM_PATTERN.match(c)]:
            df_out[col] = clip_likert(df_out[col], LIKERT_MIN, LIKERT_MAX)

        # Calcul des trois dimensions centrales du MBI.
        for dim in DIMENSIONS:
            col_name = f"{dim}_score"
            computed = compute_group_score(df_out, dim, multiplier=1)
            if computed.notna().any():
                df_out[col_name] = computed
            elif col_name not in df_out.columns:
                df_out[col_name] = np.nan

        return df_out

    def classify(self, df: pd.DataFrame) -> pd.DataFrame:
        df_out = df.copy()

        # Les dimensions ne se lisent pas toutes dans le même sens :
        # une efficacité élevée est plutôt protectrice, contrairement
        # à l'épuisement et au cynisme.
        for col, bounds in THRESHOLDS.items():
            if col not in df_out.columns:
                continue
            v = df_out[col]
            if col == "efficacy_score":
                # Logique inversée : score élevé = bon, faible = risque
                df_out[f"{col}_cat"] = np.where(
                    v.isna(), "Non renseigné",
                    np.where(v >= bounds["high"], "Bas",
                             np.where(v >= bounds["low"], "Modéré", "Élevé"))
                )
            else:
                df_out[f"{col}_cat"] = np.where(
                    v.isna(), "Non renseigné",
                    np.where(v <= bounds["low"], "Bas",
                             np.where(v <= bounds["high"], "Modéré", "Élevé"))
                )

        # Score de risque burnout composite :
        # burnout = épuisement élevé + cynisme élevé + efficacité faible.
        if all(c in df_out.columns for c in ["exhaustion_score_cat", "cynicism_score_cat", "efficacy_score_cat"]):
            risk_points = (
                (df_out["exhaustion_score_cat"] == "Élevé").astype(int) +
                (df_out["cynicism_score_cat"]   == "Élevé").astype(int) +
                (df_out["efficacy_score_cat"]   == "Élevé").astype(int)
            )
            df_out["burnout_risk"] = np.where(
                risk_points >= 3, "Élevé",
                np.where(risk_points >= 1, "Modéré", "Faible")
            )

        return df_out

    def analytics(self, df: pd.DataFrame) -> dict:
        from .analytics import MBIAnalytics
        return MBIAnalytics(df).compute()

    def count_items(self, df: pd.DataFrame) -> int:
        return sum(1 for c in df.columns if ITEM_PATTERN.match(c))
