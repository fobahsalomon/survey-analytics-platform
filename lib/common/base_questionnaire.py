"""
lib/common/base_questionnaire.py
Abstract base class for all questionnaire modules.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd


class BaseQuestionnaire(ABC):
    """
    Interface commune à tous les questionnaires.
    Chaque questionnaire doit implémenter ces méthodes pour rester compatible
    avec les pages Streamlit, les analytics, les visualisations et le reporting.
    """

    @abstractmethod
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoyage et prétraitement des données brutes."""
        ...

    @abstractmethod
    def score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcul des scores à partir des items Likert."""
        ...

    @abstractmethod
    def classify(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classification selon les seuils du questionnaire."""
        ...

    @abstractmethod
    def analytics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcul des indicateurs agrégés pour le dashboard."""
        ...

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline complet standard.

        L'idée est simple :
        1. nettoyer les données brutes ;
        2. calculer les scores ;
        3. transformer ces scores en catégories lisibles.
        """
        df = self.clean(df)
        df = self.score(df)
        df = self.classify(df)
        return df
