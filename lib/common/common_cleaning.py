# lib/common/common_cleaning.py
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class CommonCleaner:
    @staticmethod
    def clean_likert(series: pd.Series, min_val: int = 1, max_val: int = 4) -> pd.Series:
        """
        Force les valeurs dans la plage Likert [min, max].
        Recyclé depuis karasek_pipeline_wave_ci.py
        """
        s = pd.to_numeric(series, errors='coerce')
        invalid = (~s.between(min_val, max_val)) & s.notna()
        if invalid.any():
            logger.warning(f"{invalid.sum()} valeurs Likert hors plage converties en NaN")
        return s.where(s.between(min_val, max_val))

    @staticmethod
    def invert_items(df: pd.DataFrame, items: list, min_val: int = 1, max_val: int = 4) -> pd.DataFrame:
        """
        Inverse les items négatifs (ex: 1 devient 4).
        """
        df = df.copy()
        available = [c for c in items if c in df.columns]
        if available:
            df[available] = (min_val + max_val) - df[available]
            logger.info(f"Inversion appliquée sur {len(available)} items")
        return df