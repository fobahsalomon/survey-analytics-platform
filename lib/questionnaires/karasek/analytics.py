# lib/questionnaires/karasek/analytics.py
import pandas as pd
import numpy as np
from typing import Dict, Any

class KarasekAnalytics:
    def __init__(self, config):
        self.config = config

    def compute_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        metrics = {
            "demographics": self._demo_stats(df),
            "scores_continuous": self._continuous_scores(df),
            "quadrants": self._quadrant_dist(df),
            "strain_prevalence": self._strain_prevalence(df),
            "rh_scores": self._rh_scores(df)
        }
        return metrics

    def _demo_stats(self, df: pd.DataFrame) -> Dict:
        total = len(df)
        return {
            "total": total,
            "men_pct": float((df["Genre"] == "Homme").sum() / total * 100) if "Genre" in df.columns else 0,
            "women_pct": float((df["Genre"] == "Femme").sum() / total * 100) if "Genre" in df.columns else 0,
            "avg_age": float(df["Age"].mean()) if "Age" in df.columns else 0
        }

    def _continuous_scores(self, df: pd.DataFrame) -> Dict:
        res = {}
        for col in ["Dem_score", "Lat_score", "SS_score"]:
            if col in df.columns:
                s = df[col]
                res[col] = {
                    "mean": float(s.mean()),
                    "std": float(s.std()),
                    "min": float(s.min()),
                    "max": float(s.max())
                }
        return res

    def _quadrant_dist(self, df: pd.DataFrame) -> Dict:
        if "Karasek_quadrant" not in df.columns: return {}
        counts = df["Karasek_quadrant"].value_counts()
        total = len(df)
        return {
            q: {"count": int(c), "pct": float(c/total*100)} 
            for q, c in counts.items()
        }

    def _strain_prevalence(self, df: pd.DataFrame) -> Dict:
        res = {}
        for col in ["Job_strain", "Iso_strain"]:
            if col in df.columns:
                n = (df[col] == "Présent").sum()
                res[col] = {"count": int(n), "pct": float(n/len(df)*100)}
        return res

    def _rh_scores(self, df: pd.DataFrame) -> Dict:
        res = {}
        for group in self.config.RH_SCORE_GROUPS:
            col = f"{group}_score"
            cat_col = f"{col}_cat"
            if col in df.columns:
                # % Niveau élevé
                if cat_col in df.columns:
                    high = (df[cat_col] == "Élevé").sum()
                else:
                    # Fallback seuil
                    th = self.config.THRESHOLDS.get(col, 0)
                    high = (df[col] > th).sum()
                
                res[group] = {"pct_high": float(high/len(df)*100)}
        return res