# backend/services/report_service.py
from pathlib import Path
from typing import Optional
from fastapi import HTTPException
from core.config import config
from core.logger import logger

class ReportService:
    """
    Service de gestion des rapports et fichiers générés.
    """
    
    @staticmethod
    def get_report_path(
        questionnaire_type: str,
        session_id: str,
        filename: str = "rapport_karasek.docx"
    ) -> Optional[Path]:
        """
        Récupère le chemin d'un rapport généré.
        """
        reports_dir = config.REPORTS_DIR / questionnaire_type
        if not reports_dir.exists():
            return None
        
        # Chercher le dossier de session
        for folder in reports_dir.iterdir():
            if folder.is_dir() and session_id in folder.name:
                report_path = folder / filename
                if report_path.exists():
                    return report_path
        
        return None
    
    @staticmethod
    def get_figure_path(
        questionnaire_type: str,
        session_id: str,
        figure_name: str
    ) -> Optional[Path]:
        """
        Récupère le chemin d'une figure générée.
        """
        reports_dir = config.REPORTS_DIR / questionnaire_type
        if not reports_dir.exists():
            return None
        
        for folder in reports_dir.iterdir():
            if folder.is_dir() and session_id in folder.name:
                figures_dir = folder / "figures"
                if figures_dir.exists():
                    # Chercher la figure (avec ou sans extension)
                    for ext in ["", ".png", ".jpg", ".svg"]:
                        figure_path = figures_dir / f"{figure_name}{ext}"
                        if figure_path.exists():
                            return figure_path
        
        return None
    
    @staticmethod
    def cleanup_old_reports(max_age_hours: int = 24) -> int:
        """
        Nettoie les rapports anciens (optionnel, pour maintenance).
        """
        import time
        cleaned = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for questionnaire_type in config.SUPPORTED_QUESTIONNAIRES:
            q_dir = config.REPORTS_DIR / questionnaire_type
            if not q_dir.exists():
                continue
            
            for folder in q_dir.iterdir():
                if folder.is_dir():
                    folder_time = folder.stat().st_mtime
                    if current_time - folder_time > max_age_seconds:
                        # Supprimer le dossier
                        import shutil
                        shutil.rmtree(folder)
                        cleaned += 1
                        logger.info(f"Nettoyé: {folder}")
        
        return cleaned