# backend/api/controllers.py
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException
from core.config import config
from core.logger import logger
from services.pipeline_service import PipelineService
from services.report_service import ReportService

class AnalysisController:
    """
    Contrôleur pour les endpoints d'analyse.
    Valide les requêtes et appelle les services.
    """
    
    def __init__(self):
        self.pipeline_service = PipelineService()
        self.report_service = ReportService()
    
    async def validate_file(self, file: UploadFile) -> Path:
        """
        Valide et sauvegarde le fichier uploadé.
        """
        # Vérifier l'extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nom de fichier manquant")
        
        ext = Path(file.filename).suffix.lower()
        if ext not in [f".{e}" for e in config.ALLOWED_EXTENSIONS]:
            raise HTTPException(
                status_code=400,
                detail=f"Extension non autorisée. Autorisées: {config.ALLOWED_EXTENSIONS}"
            )
        
        # Vérifier la taille (lire le contenu pour vérifier)
        content = await file.read()
        if len(content) > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Fichier trop volumineux. Max: {config.MAX_FILE_SIZE / 1024 / 1024} MB"
            )
        
        # Sauvegarder le fichier
        upload_path = config.UPLOAD_DIR / file.filename
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(upload_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Fichier uploadé: {file.filename} ({len(content)} bytes)")
        return upload_path
    
    async def start_analysis(
        self,
        questionnaire_type: str,
        file: UploadFile
    ) -> Dict[str, Any]:
        """
        Démarre une analyse complète.
        """
        # Valider le type de questionnaire
        if questionnaire_type not in config.SUPPORTED_QUESTIONNAIRES:
            raise HTTPException(
                status_code=400,
                detail=f"Questionnaire non supporté. Supportés: {config.SUPPORTED_QUESTIONNAIRES}"
            )
        
        # Valider et sauvegarder le fichier
        file_path = await self.validate_file(file)
        
        # Exécuter le pipeline
        results = self.pipeline_service.run_analysis(
            questionnaire_type=questionnaire_type,
            file_path=str(file_path),
        )
        
        if results.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=results.get("error_message", "Erreur pendant l'analyse")
            )
        
        return results
    
    def get_analysis_results(
        self,
        questionnaire_type: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Récupère les résultats d'une analyse existante.
        """
        # Vérifier que le rapport existe
        report_path = self.report_service.get_report_path(
            questionnaire_type, session_id
        )
        
        if not report_path:
            raise HTTPException(
                status_code=404,
                detail="Analyse non trouvée ou expirée"
            )
        
        # Retourner les métadonnées (le frontend devrait avoir gardé les metrics)
        return {
            "session_id": session_id,
            "questionnaire_type": questionnaire_type,
            "report_available": True,
            "report_download_url": f"/api/reports/{questionnaire_type}/{session_id}/rapport_karasek.docx",
        }
    
    def get_questionnaire_info(self, questionnaire_type: str) -> Dict[str, Any]:
        """
        Retourne les informations d'un questionnaire.
        """
        return self.pipeline_service.get_questionnaire_info(questionnaire_type)
    
    def download_report(
        self,
        questionnaire_type: str,
        session_id: str,
        filename: str = "rapport_karasek.docx"
    ) -> Path:
        """
        Prépare le téléchargement d'un rapport.
        """
        report_path = self.report_service.get_report_path(
            questionnaire_type, session_id, filename
        )
        
        if not report_path:
            raise HTTPException(
                status_code=404,
                detail="Rapport non trouvé"
            )
        
        return report_path
    
    def get_figure(
        self,
        questionnaire_type: str,
        session_id: str,
        figure_name: str
    ) -> Path:
        """
        Récupère une figure générée.
        """
        figure_path = self.report_service.get_figure_path(
            questionnaire_type, session_id, figure_name
        )
        
        if not figure_path:
            raise HTTPException(
                status_code=404,
                detail="Figure non trouvée"
            )
        
        return figure_path


# Instance globale
analysis_controller = AnalysisController()