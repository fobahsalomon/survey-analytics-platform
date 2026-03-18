"""
lib/questionnaires/karasek/analytics.py
Calcul des indicateurs agrégés Karasek pour le dashboard et le rapport.
"""

import re
import numpy as np
import pandas as pd
from typing import Dict, Any

from lib.common import normalize_col, find_col_by_pattern
from .config import THRESHOLDS, SCORE_LABELS, RH_SCORE_GROUPS


class KarasekAnalytics:
    """Calcule tous les indicateurs statistiques du modèle Karasek."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    # ─── helpers ────────────────────────────────────────────────────────────

    def _pct_high(self, score_col: str) -> tuple[float, int, int]:
        """Retourne (pct_élevé, n_élevé, n_total) pour un score."""
        cat = f"{score_col}_theo_cat"
        if cat in self.df.columns:
            v = self.df[cat].dropna()
            n_h = int(v.isin(["Élevé", "Eleve", "Elevé", "High"]).sum())
            return (float(n_h / len(v) * 100) if len(v) > 0 else 0.0), n_h, int(len(v))
        if score_col in self.df.columns:
            v = pd.to_numeric(self.df[score_col], errors="coerce").dropna()
            t = THRESHOLDS.get(score_col)
            n_h = int((v > t).sum()) if t is not None else 0
            return (float(n_h / len(v) * 100) if len(v) > 0 else 0.0), n_h, int(len(v))
        return 0.0, 0, 0

    def _strain_prevalence(self, col: str) -> tuple[float, int]:
        if col not in self.df.columns:
            return 0.0, 0
        v = self.df[col].dropna()
        n = int((v == "Présent").sum())
        return (float(n / len(v) * 100) if len(v) > 0 else 0.0), n

    # ─── données démographiques ──────────────────────────────────────────────

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

    # ─── modes de vie ────────────────────────────────────────────────────────

    def _lifestyle(self) -> Dict[str, Any]:
        df = self.df
        total = len(df)
        result = {}

        tabac_col = find_col_by_pattern(list(df.columns), [r"tabag"])
        alcool_col = next((c for c in df.columns if re.search(r"consommation.*alcool|alcool", normalize_col(c))), None)
        sport_col = find_col_by_pattern(list(df.columns), [r"pratique.*sport", r"\bsport\b"])
        chronic_col = next((c for c in df.columns if re.search(r"maladie.*chron", normalize_col(c))), None)

        for key, col, val in [
            ("tobacco", tabac_col, "oui"),
            ("alcohol", alcool_col, "oui"),
        ]:
            if col and col in df.columns:
                s = df[col].astype(str).str.strip().str.lower()
                n = int((s == val).sum())
                result[key] = {"n": n, "pct": n / total * 100 if total else 0.0}

        if sport_col and sport_col in df.columns:
            s = df[sport_col].astype(str).str.strip().str.lower()
            n = int((s == "non").sum())
            result["sedentarity"] = {"n": n, "pct": n / total * 100 if total else 0.0}

        if chronic_col and chronic_col in df.columns:
            s = df[chronic_col].astype(str).str.strip().str.lower()
            n = int((s == "oui").sum())
            result["chronic"] = {"n": n, "pct": n / total * 100 if total else 0.0}

        if "IMC_binaire" in df.columns:
            n = int((df["IMC_binaire"].astype(str).str.strip() == "Surpoids/Obésité").sum())
            result["overweight"] = {"n": n, "pct": n / total * 100 if total else 0.0}

        return result

    # ─── quadrants ──────────────────────────────────────────────────────────

    def _quadrants(self) -> Dict[str, Any]:
        quad_col = "Karasek_quadrant_theoretical"
        if quad_col not in self.df.columns:
            return {}
        v = self.df[quad_col].dropna()
        tv = len(v)
        aliases = {
            "Tendu":   ["Tendu", "Tense"],
            "Actif":   ["Actif", "Active"],
            "Passif":  ["Passif", "Passive"],
            "Détendu": ["Detendu", "Détendu", "Relaxed"],
        }
        result = {}
        for name, alts in aliases.items():
            count = int(v.isin(alts).sum())
            result[name] = {"count": count, "pct": count / tv * 100 if tv else 0.0}
        return result

    # ─── stress indicators ───────────────────────────────────────────────────

    def _stress_indicators(self) -> Dict[str, Any]:
        pct_lat, n_lat, _ = self._pct_high("Lat_score")
        pct_dem, n_dem, _ = self._pct_high("Dem_score")
        pct_ss, n_ss, _ = self._pct_high("SS_score")
        return {
            "autonomy":       {"pct": pct_lat, "n": n_lat},
            "workload":       {"pct": pct_dem, "n": n_dem},
            "social_support": {"pct": pct_ss,  "n": n_ss},
        }

    # ─── strain prevalence ───────────────────────────────────────────────────

    def _strain_prev(self) -> Dict[str, Any]:
        pct_js, n_js = self._strain_prevalence("Job_strain_theoretical")
        pct_is, n_is = self._strain_prevalence("Iso_strain_theoretical")
        return {
            "Job_strain": {"pct": pct_js, "n": n_js},
            "Iso_strain": {"pct": pct_is, "n": n_is},
        }

    # ─── RH scores ──────────────────────────────────────────────────────────

    def _rh_scores(self) -> Dict[str, Any]:
        result = {}
        rh_cols = [f"{g}_score" for g in RH_SCORE_GROUPS] + ["comp_score", "auto_score", "sup_score"]
        for col in rh_cols:
            pct, n, total = self._pct_high(col)
            if total > 0:
                result[col] = {
                    "label": SCORE_LABELS.get(col, col),
                    "pct":   pct,
                    "n":     n,
                    "total": total,
                }
        return result

    # ─── point d'entrée ─────────────────────────────────────────────────────

    def compute(self) -> Dict[str, Any]:
        return {
            "demographics":      self._demographics(),
            "lifestyle":         self._lifestyle(),
            "quadrants":         self._quadrants(),
            "stress_indicators": self._stress_indicators(),
            "strain_prevalence": self._strain_prev(),
            "rh_scores":         self._rh_scores(),
        }
