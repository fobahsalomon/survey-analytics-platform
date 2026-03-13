import pandas as pd
import numpy as np
from typing import Dict, Any

class KarasekAnalytics:
    def __init__(self, config):
        self.config = config

    def compute_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        metrics = {
            "demographics": self._demo_stats(df),
            "lifestyle": self._lifestyle_stats(df),
            "scores_continuous": self._continuous_scores(df),
            "quadrants": self._quadrant_dist(df),
            "strain_prevalence": self._strain_prevalence(df),
            "stress_indicators": self._stress_indicators(df),
            "rh_scores": self._rh_scores(df)
        }
        return metrics

    def _demo_stats(self, df: pd.DataFrame) -> Dict:
        total = len(df)
        n_men = int((df["Genre"].astype(str).str.lower().isin(["homme", "male", "m"])).sum()) if "Genre" in df.columns else 0
        n_women = int((df["Genre"].astype(str).str.lower().isin(["femme", "female", "f"])).sum()) if "Genre" in df.columns else 0
        avg_age = float(df["Age"].mean()) if "Age" in df.columns else 0.0
        
        return {
            "total": total,
            "men": {"n": n_men, "pct": float(n_men/total*100) if total > 0 else 0},
            "women": {"n": n_women, "pct": float(n_women/total*100) if total > 0 else 0},
            "avg_age": round(avg_age, 1)
        }

    def _lifestyle_stats(self, df: pd.DataFrame) -> Dict:
        total = len(df)
        res = {}
        
        # Sport (Non = Sédentarité)
        col_sport = "Pratique reguliere du sport"
        if col_sport in df.columns:
            n = int((df[col_sport].astype(str).str.lower() == "non").sum())
            res["sedentarity"] = {"n": n, "pct": float(n/total*100) if total > 0 else 0}
        
        # Alcool (Oui)
        col_alcool = next((c for c in ["Consommation reguliere d'alcool", "Consommation reguliere d\u2019alcool"] if c in df.columns), None)
        if col_alcool:
            n = int((df[col_alcool].astype(str).str.lower() == "oui").sum())
            res["alcohol"] = {"n": n, "pct": float(n/total*100) if total > 0 else 0}
        
        # Tabagisme (Oui)
        if "tabagisme" in df.columns:
            n = int((df["tabagisme"].astype(str).str.lower() == "oui").sum())
            res["tobacco"] = {"n": n, "pct": float(n/total*100) if total > 0 else 0}
        
        # Maladie chronique (Oui)
        col_chronic = "Avez-vous une maladie chronique"
        if col_chronic in df.columns:
            n = int((df[col_chronic].astype(str).str.lower() == "oui").sum())
            res["chronic"] = {"n": n, "pct": float(n/total*100) if total > 0 else 0}
        
        # Surpoids/Obésité
        if "IMC_binaire" in df.columns:
            n = int((df["IMC_binaire"].astype(str).str.contains("Surpoids|Obésité", na=False)).sum())
            res["overweight"] = {"n": n, "pct": float(n/total*100) if total > 0 else 0}
        
        return res

    def _continuous_scores(self, df: pd.DataFrame) -> Dict:
        res = {}
        for col in ["Dem_score", "Lat_score", "SS_score"]:
            if col in df.columns:
                s = df[col]
                res[col] = {
                    "mean": round(float(s.mean()), 2),
                    "std": round(float(s.std()), 2),
                    "min": round(float(s.min()), 1),
                    "max": round(float(s.max()), 1)
                }
        return res

    def _quadrant_dist(self, df: pd.DataFrame) -> Dict:
        # Priorité à la colonne theoretical
        col = "Karasek_quadrant_theoretical" if "Karasek_quadrant_theoretical" in df.columns else "Karasek_quadrant"
        if col not in df.columns: return {}
        
        counts = df[col].value_counts()
        total = len(df)
        return {
            q: {"count": int(c), "pct": round(float(c/total*100), 1)} 
            for q, c in counts.items()
        }

    def _strain_prevalence(self, df: pd.DataFrame) -> Dict:
        res = {}
        for col in ["Job_strain_theoretical", "Job_strain"]:
            if col in df.columns:
                n = int((df[col] == "Présent").sum())
                res["Job_strain"] = {"n": n, "pct": round(float(n/len(df)*100), 1)}
                break
        
        for col in ["Iso_strain_theoretical", "Iso_strain"]:
            if col in df.columns:
                n = int((df[col] == "Présent").sum())
                res["Iso_strain"] = {"n": n, "pct": round(float(n/len(df)*100), 1)}
                break
        return res

    def _stress_indicators(self, df: pd.DataFrame) -> Dict:
        """
        Pourcentage et effectif avec niveau ÉLEVÉ pour:
        - Autonomie (Lat_score)
        - Charge mentale (Dem_score)
        - Soutien social (SS_score)
        """
        res = {}
        indicators = {
            "autonomy": "Lat_score",
            "workload": "Dem_score",
            "social_support": "SS_score"
        }
        
        for key, col in indicators.items():
            if col in df.columns:
                threshold = self.config.THRESHOLDS.get(col, 0)
                n = int((df[col] > threshold).sum())
                res[key] = {"n": n, "pct": round(float(n/len(df)*100), 1)}
        
        return res

    def _rh_scores(self, df: pd.DataFrame) -> Dict:
        """
        Pourcentage et effectif avec niveau ÉLEVÉ pour les 8 dimensions RH
        """
        res = {}
        rh_dimensions = {
            "rec_score": "Reconnaissance",
            "equ_score": "Équité de charge",
            "cult_score": "Culture d'entreprise",
            "sat_score": "Satisfaction",
            "adq_resources_score": "Ressources & Objectifs",
            "sup_score": "Soutien management",
            "adq_role_score": "Formation",
            "comp_score": "Compétences"
        }
        
        for col, label in rh_dimensions.items():
            if col in df.columns:
                threshold = self.config.THRESHOLDS.get(col, 0)
                n = int((df[col] > threshold).sum())
                res[col] = {
                    "label": label,
                    "n": n,
                    "pct": round(float(n/len(df)*100), 1)
                }
        
        return res