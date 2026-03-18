"""
lib/questionnaires/qvt/analytics.py
Indicateurs agrégés QVT.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any

from lib.common import compute_average_age
from .config import DIMENSIONS, THRESHOLDS, SCORE_LABELS, QVT_COLORS


class QVTAnalytics:
    """Calcule les indicateurs agrégés du questionnaire QVT."""
    def __init__(self, df: pd.DataFrame):
        """Stocke le DataFrame déjà nettoyé et scoré."""
        self.df = df

    def _pct_cat(self, score_col: str, category: str) -> tuple[float, int, int]:
        """Retourne le pourcentage et l'effectif d'une catégorie de score."""
        cat_col = f"{score_col}_cat"
        if cat_col not in self.df.columns:
            return 0.0, 0, 0
        v = self.df[cat_col].dropna()
        n = int((v == category).sum())
        total = len(v)
        return float(n / total * 100) if total else 0.0, n, total

    def _dimension_summary(self) -> Dict[str, Any]:
        """Calcule les statistiques résumées de chaque dimension QVT."""
        result = {}
        for dim in DIMENSIONS:
            col = f"{dim}_score"
            cat_col = f"{col}_cat"
            if col in self.df.columns:
                v = pd.to_numeric(self.df[col], errors="coerce").dropna()
                cats = {}
                for cat in ["Satisfaisant", "Mitigé", "Insatisfaisant"]:
                    pct, n, total = self._pct_cat(col, cat)
                    cats[cat] = {"pct": pct, "n": n}
                result[dim] = {
                    "label":  DIMENSIONS[dim],
                    "mean":   round(float(v.mean()), 2) if len(v) else 0.0,
                    "median": round(float(v.median()), 2) if len(v) else 0.0,
                    "n":      len(v),
                    "categories": cats,
                }
        return result

    def _global_summary(self) -> Dict[str, Any]:
        """Calcule les statistiques du score QVT global."""
        col = "qvt_global_score"
        if col not in self.df.columns:
            return {}
        v = pd.to_numeric(self.df[col], errors="coerce").dropna()
        if v.empty:
            return {}
        return {
            "mean":   round(float(v.mean()), 2),
            "median": round(float(v.median()), 2),
            "n":      len(v),
            "pct_satisfaisant": float((v >= THRESHOLDS[col]).sum() / len(v) * 100),
        }

    def _demographics(self) -> Dict[str, Any]:
        """Calcule les indicateurs démographiques de base."""
        df = self.df
        total = len(df)
        gs = df["Genre"].astype(str).str.strip().str.lower() if "Genre" in df.columns else pd.Series(dtype=str)
        n_men = int(gs.isin({"homme", "male", "m"}).sum()) if not gs.empty else 0
        n_women = int(gs.isin({"femme", "female", "f"}).sum()) if not gs.empty else 0
        # On ne suppose pas que le fichier contient toujours un âge exact.
        avg_age = compute_average_age(df)
        return {
            "total": total,
            "men": {"n": n_men, "pct": n_men / total * 100 if total else 0.0},
            "women": {"n": n_women, "pct": n_women / total * 100 if total else 0.0},
            "avg_age": avg_age,
        }

    def compute(self) -> Dict[str, Any]:
        """Retourne le paquet complet de métriques QVT pour le dashboard."""
        return {
            "demographics":   self._demographics(),
            "dimensions":     self._dimension_summary(),
            "global":         self._global_summary(),
        }
