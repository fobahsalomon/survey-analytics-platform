import pandas as pd
import numpy as np
from pathlib import Path
from lib.common.base_questionnaire import BaseQuestionnaire
from lib.common.common_cleaning import CommonCleaner
from lib.common.file_utils import FileUtils
from .config import KarasekConfig
import logging

logger = logging.getLogger(__name__)

class KarasekQuestionnaire(BaseQuestionnaire):
    def __init__(self):
        super().__init__(KarasekConfig())
        self.cleaner = CommonCleaner()

    def load_data(self, file_path: str) -> pd.DataFrame:
        return FileUtils.load_csv_robust(file_path)

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # 1. Renommage
        mapping = {k: v for k, v in self.config.RENAME_MAPPING.items() if k in df.columns}
        if mapping:
            df = df.rename(columns=mapping)
        
        # 2. Nettoyage Likert (Colonnes commençant par Q)
        likert_cols = [c for c in df.columns if c.startswith("Q") and "_" in c]
        for col in likert_cols:
            df[col] = self.cleaner.clean_likert(df[col])
            
        # 3. Inversion
        df = self.cleaner.invert_items(df, self.config.INVERT_ITEMS)
        
        return df

    def score(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Fonction interne pour calculer les scores de groupe
        def compute_group_score(suffix: str, multiplier: int = 1, normalize: bool = True):
            cols = [c for c in df.columns if c.endswith(f"_{suffix}")]
            if not cols: return pd.Series(np.nan, index=df.index, name=f"{suffix}_score")
            
            ssum = df[cols].sum(axis=1, skipna=True)
            n_answered = df[cols].notna().sum(axis=1)
            n_items = len(cols)
            
            with np.errstate(invalid='ignore', divide='ignore'):
                score = (ssum / n_answered.replace(0, np.nan) * n_items * multiplier) if normalize else ssum * multiplier
            
            return score.where(n_answered > 0, np.nan)

        # 1. Scores Karasek de base
        for group, mult in self.config.SCORE_MULTIPLIERS.items():
            df[f"{group}_score"] = compute_group_score(group, multiplier=mult, normalize=True)
        
        # 2. Scores Composites (Dem, Lat, SS)
        for name, comps in self.config.KARASEK_SCORE_COMPOSITION.items():
            existing = [c for c in comps if c in df.columns]
            df[name] = sum(df[c] for c in existing) if existing else np.nan
            
        # 3. Scores RH
        for group in self.config.RH_SCORE_GROUPS:
            df[f"{group}_score"] = compute_group_score(group, multiplier=1, normalize=True)
            
        return df

    def classify(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classification UNIQUEMENT par seuils théoriques.
        Suppression de la logique 'internal' pour ce projet portfolio.
        """
        df = df.copy()
        th = self.config.THRESHOLDS
        
        dem_th = th.get("Dem_score", 22.5)
        lat_th = th.get("Lat_score", 60.0)
        ss_th  = th.get("SS_score", 20.0)
        
        # Quadrants
        conditions = [
            (df["Lat_score"] >= lat_th) & (df["Dem_score"] >= dem_th), # Actif
            (df["Lat_score"] >= lat_th) & (df["Dem_score"] <  dem_th), # Detendu
            (df["Lat_score"] <  lat_th) & (df["Dem_score"] >= dem_th), # Tendu
        ]
        choices = ["Actif", "Detendu", "Tendu"]
        df["Karasek_quadrant"] = np.select(conditions, choices, default="Passif")
        
        # Job Strain
        df["Job_strain"] = np.where(
            (df["Dem_score"] >= dem_th) & (df["Lat_score"] < lat_th), 
            "Présent", "Absent"
        )
        
        # Iso Strain
        df["Iso_strain"] = np.where(
            (df["Dem_score"] >= dem_th) & (df["SS_score"] < ss_th), 
            "Présent", "Absent"
        )
        
        # Catégorisation binaire des scores (Faible / Élevé)
        for col, threshold in th.items():
            if col in df.columns:
                cat_col = f"{col}_cat"
                df[cat_col] = np.where(
                    df[col].isna(), "Non renseigné",
                    np.where(df[col] <= threshold, "Faible", "Élevé")
                )
                
        return df

    def analyze(self, df: pd.DataFrame) -> dict:
        # Délègue à la classe Analytics pour garder questionnaire.py propre
        from .analytics import KarasekAnalytics
        analyzer = KarasekAnalytics(self.config)
        return analyzer.compute_metrics(df)

    def generate_report(self, df: pd.DataFrame, metrics: dict, output_dir: str) -> str:
            from .reporting import KarasekReporting
            from .visualization import KarasekVisualizer
            
            # 1. Générer les graphiques d'abord
            visualizer = KarasekVisualizer(self.config)
            figures = visualizer.generate_all_plots(df)
            
            # 2. Générer le rapport Word (avec chemins des figures)
            reporter = KarasekReporting(self.config)
            return reporter.generate_word_report(df, metrics, output_dir, figures)