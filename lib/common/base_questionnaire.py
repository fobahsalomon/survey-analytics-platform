from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

class BaseQuestionnaire(ABC):
    """
    Interface de base pour tous les questionnaires.
    Assure une structure cohérente pour le chargement, le scoring et l'analyse.
    """
    
    def __init__(self, config: Any):
        self.config = config
        self.df: Optional[pd.DataFrame] = None
        self.metrics: Dict[str, Any] = {}

    @abstractmethod
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Charge et retourne le DataFrame brut."""
        pass

    @abstractmethod
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoyage spécifique (Likert, inversions, etc.)."""
        pass

    @abstractmethod
    def score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcul des scores composites."""
        pass

    @abstractmethod
    def classify(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classification (ex: Quadrants Karasek)."""
        pass

    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Génération des indicateurs statistiques."""
        pass

    @abstractmethod
    def generate_report(self, df: pd.DataFrame, metrics: Dict, output_path: str) -> str:
        """Génération du rapport (Word/PDF)."""
        pass

    def run_pipeline(self, input_file: str, output_dir: str) -> Dict[str, Any]:
        """Orchestration complète du pipeline."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 1. Load
        self.df = self.load_data(input_file)
        
        # 2. Clean
        self.df = self.clean(self.df)
        
        # 3. Score
        self.df = self.score(self.df)
        
        # 4. Classify
        self.df = self.classify(self.df)
        
        # 5. Analyze
        self.metrics = self.analyze(self.df)
        
        # 6. Report
        report_path = self.generate_report(self.df, self.metrics, output_dir)
        
        return {
            "status": "success",
            "rows": len(self.df),
            "metrics": self.metrics,
            "report_path": report_path
        }