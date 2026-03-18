"""
lib/questionnaires/mbi/analytics.py
Indicateurs agrégés MBI.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any

from .config import DIMENSIONS, THRESHOLDS, SCORE_LABELS


class MBIAnalytics:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def _cat_distribution(self, col: str) -> Dict[str, Any]:
        cat_col = f"{col}_cat"
        if cat_col not in self.df.columns:
            return {}
        v = self.df[cat_col].dropna()
        total = len(v)
        result = {}
        for cat in ["Bas", "Modéré", "Élevé"]:
            n = int((v == cat).sum())
            result[cat] = {"n": n, "pct": n / total * 100 if total else 0.0}
        return result

    def _demographics(self) -> Dict[str, Any]:
        df = self.df
        total = len(df)
        gs = df["Genre"].astype(str).str.strip().str.lower() if "Genre" in df.columns else pd.Series(dtype=str)
        n_men = int(gs.isin({"homme", "male", "m"}).sum()) if not gs.empty else 0
        n_women = int(gs.isin({"femme", "female", "f"}).sum()) if not gs.empty else 0
        avg_age = round(float(pd.to_numeric(df["Age"], errors="coerce").mean()), 1) if "Age" in df.columns else 0.0
        return {
            "total": total,
            "men": {"n": n_men, "pct": n_men / total * 100 if total else 0.0},
            "women": {"n": n_women, "pct": n_women / total * 100 if total else 0.0},
            "avg_age": avg_age,
        }

    def _dimensions(self) -> Dict[str, Any]:
        result = {}
        for dim in DIMENSIONS:
            col = f"{dim}_score"
            if col in self.df.columns:
                v = pd.to_numeric(self.df[col], errors="coerce").dropna()
                result[dim] = {
                    "label":        DIMENSIONS[dim],
                    "mean":         round(float(v.mean()), 2) if len(v) else 0.0,
                    "n":            len(v),
                    "categories":   self._cat_distribution(col),
                }
        return result

    def _burnout_risk(self) -> Dict[str, Any]:
        if "burnout_risk" not in self.df.columns:
            return {}
        v = self.df["burnout_risk"].dropna()
        total = len(v)
        result = {}
        for level in ["Faible", "Modéré", "Élevé"]:
            n = int((v == level).sum())
            result[level] = {"n": n, "pct": n / total * 100 if total else 0.0}
        return result

    def compute(self) -> Dict[str, Any]:
        return {
            "demographics":  self._demographics(),
            "dimensions":    self._dimensions(),
            "burnout_risk":  self._burnout_risk(),
        }
