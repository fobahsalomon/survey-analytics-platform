"""
lib/questionnaires/mbi/analytics.py
Indicateurs agrégés MBI.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any

from lib.common import compute_average_age
from .config import DIMENSIONS, THRESHOLDS, SCORE_LABELS


class MBIAnalytics:
    """Calcule les indicateurs agrégés du questionnaire MBI."""
    def __init__(self, df: pd.DataFrame):
        """Stocke le DataFrame déjà nettoyé et scoré."""
        self.df = df

    def _cat_distribution(self, col: str) -> Dict[str, Any]:
        """Retourne la répartition Bas/Modéré/Élevé d'une dimension MBI."""
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
        """Calcule les indicateurs démographiques de base."""
        df = self.df
        total = len(df)
        gs = df["Genre"].astype(str).str.strip().str.lower() if "Genre" in df.columns else pd.Series(dtype=str)
        n_men = int(gs.isin({"homme", "male", "m"}).sum()) if not gs.empty else 0
        n_women = int(gs.isin({"femme", "female", "f"}).sum()) if not gs.empty else 0
        # Même logique de fallback que pour les autres modules.
        avg_age = compute_average_age(df)
        return {
            "total": total,
            "men": {"n": n_men, "pct": n_men / total * 100 if total else 0.0},
            "women": {"n": n_women, "pct": n_women / total * 100 if total else 0.0},
            "avg_age": avg_age,
        }

    def _dimensions(self) -> Dict[str, Any]:
        """Calcule les statistiques résumées des dimensions MBI."""
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
        """Calcule la répartition du risque de burnout composite."""
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
        """Retourne le paquet complet de métriques MBI pour le dashboard."""
        return {
            "demographics":  self._demographics(),
            "dimensions":    self._dimensions(),
            "burnout_risk":  self._burnout_risk(),
        }
