# backend/services/pipeline_service.py
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from lib import KarasekQuestionnaire
from core.config import config
from core.logger import logger

class PipelineService:
    """
    Service d'orchestration du pipeline d'analyse.
    Appelle la bibliothèque analytics (lib/) pour traiter les questionnaires.
    """
    
    def __init__(self):
        self.questionnaire_map = {
            "karasek": KarasekQuestionnaire,
            # "qvt": QVTQuestionnaire,      # À implémenter
            # "mbi": MBIQuestionnaire,      # À implémenter
        }
    
    def run_analysis(
        self,
        questionnaire_type: str,
        file_path: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exécute le pipeline d'analyse complet.
        
        Args:
            questionnaire_type: Type de questionnaire (karasek, qvt, mbi)
            file_path: Chemin vers le fichier CSV uploadé
            session_id: Identifiant unique pour la session (optionnel)
        
        Returns:
            Dict contenant metrics, report_path, figures_dir, status
        """
        if questionnaire_type not in self.questionnaire_map:
            raise ValueError(
                f"Questionnaire '{questionnaire_type}' non supporté. "
                f"Supportés: {list(self.questionnaire_map.keys())}"
            )
        
        # Générer un session_id si non fourni
        if not session_id:
            session_id = str(uuid.uuid4())[:8]
        
        # Préparer les répertoires de sortie
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = config.REPORTS_DIR / questionnaire_type / f"{session_id}_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Démarrage analyse {questionnaire_type} | Session: {session_id}")
        
        try:
            # Initialiser le questionnaire
            questionnaire_class = self.questionnaire_map[questionnaire_type]
            questionnaire = questionnaire_class()
            
            # Exécuter le pipeline
            results = questionnaire.run_pipeline(
                input_file=file_path,
                output_dir=str(output_dir)
            )
            
            # Enrichir les résultats
            results["session_id"] = session_id
            results["questionnaire_type"] = questionnaire_type
            results["timestamp"] = timestamp
            results["status"] = "success"
            
            # Chemins pour le frontend
            results["report_download_url"] = f"/api/reports/{questionnaire_type}/{session_id}_{timestamp}/rapport_karasek.docx"
            results["figures_base_path"] = str(output_dir / "figures")
            
            logger.info(f"Analyse terminée | Lignes: {results.get('rows', 0)} | Session: {session_id}")
            
            return results
            
        except Exception as e:
            logger.error(f"Échec analyse {questionnaire_type}: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error_message": str(e),
                "session_id": session_id,
                "questionnaire_type": questionnaire_type,
            }
    
    def get_questionnaire_info(self, questionnaire_type: str) -> Dict[str, Any]:
        """
        Retourne les métadonnées d'un questionnaire.
        """
        info_map = {
            "karasek": {
                "name": "Karasek",
                "description": "Modèle Demande-Contrôle-Soutien pour l'évaluation du stress au travail",
                "dimensions": ["Demande psychologique", "Latitude décisionnelle", "Soutien social"],
                "outputs": ["Quadrants Karasek", "Job Strain", "Iso Strain", "Scores RH"],
            },
            "qvt": {
                "name": "QVT",
                "description": "Qualité de Vie au Travail - Évaluation globale du bien-être",
                "dimensions": ["Environnement", "Relations", "Développement"],
                "outputs": ["Scores composites", "Recommandations"],
            },
            "mbi": {
                "name": "MBI",
                "description": "Maslach Burnout Inventory - Évaluation de l'épuisement professionnel",
                "dimensions": ["Épuisement émotionnel", "Dépersonnalisation", "Accomplissement personnel"],
                "outputs": ["Niveaux de burnout", "Recommandations"],
            },
        }
        return info_map.get(questionnaire_type, {})