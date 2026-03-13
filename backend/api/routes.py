# backend/api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, Any, List
from core.config import config
from core.logger import logger
from api.controllers import analysis_controller

router = APIRouter(prefix="/api", tags=["Questionnaire Analytics"])

# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS PRINCIPAUX
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/questionnaires")
async def list_questionnaires() -> Dict[str, List[str]]:
    """
    Liste les questionnaires supportés.
    """
    return {
        "supported": config.SUPPORTED_QUESTIONNAIRES,
        "info": {
            q: analysis_controller.get_questionnaire_info(q)
            for q in config.SUPPORTED_QUESTIONNAIRES
        }
    }

@router.get("/questionnaires/{questionnaire_type}")
async def get_questionnaire_info(questionnaire_type: str) -> Dict[str, Any]:
    """
    Retourne les détails d'un questionnaire spécifique.
    """
    if questionnaire_type not in config.SUPPORTED_QUESTIONNAIRES:
        raise HTTPException(
            status_code=400,
            detail=f"Questionnaire non supporté. Supportés: {config.SUPPORTED_QUESTIONNAIRES}"
        )
    
    return analysis_controller.get_questionnaire_info(questionnaire_type)

@router.post("/analyze/{questionnaire_type}")
async def start_analysis(
    questionnaire_type: str,
    file: UploadFile = File(..., description="Fichier CSV à analyser")
) -> Dict[str, Any]:
    """
    Démarre l'analyse d'un questionnaire.
    
    - **questionnaire_type**: Type de questionnaire (karasek, qvt, mbi)
    - **file**: Fichier CSV contenant les données
    
    Retourne les metrics, le chemin du rapport et des figures.
    """
    logger.info(f"Requête analyse reçue: {questionnaire_type} | Fichier: {file.filename}")
    
    try:
        results = await analysis_controller.start_analysis(
            questionnaire_type=questionnaire_type,
            file=file,
        )
        
        return {
            "status": "success",
            "data": results,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur analyse: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{questionnaire_type}/{session_id}")
async def get_results(
    questionnaire_type: str,
    session_id: str
) -> Dict[str, Any]:
    """
    Récupère les résultats d'une analyse existante.
    """
    try:
        results = analysis_controller.get_analysis_results(
            questionnaire_type=questionnaire_type,
            session_id=session_id,
        )
        
        return {
            "status": "success",
            "data": results,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération résultats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS DE TÉLÉCHARGEMENT
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/reports/{questionnaire_type}/{session_id}/{filename}")
async def download_report(
    questionnaire_type: str,
    session_id: str,
    filename: str
):
    """
    Télécharge le rapport Word généré.
    """
    try:
        report_path = analysis_controller.download_report(
            questionnaire_type=questionnaire_type,
            session_id=session_id,
            filename=filename,
        )
        
        return FileResponse(
            path=str(report_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur téléchargement rapport: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/figures/{questionnaire_type}/{session_id}/{figure_name}")
async def get_figure(
    questionnaire_type: str,
    session_id: str,
    figure_name: str
):
    """
    Récupère une figure générée (PNG).
    """
    try:
        figure_path = analysis_controller.get_figure(
            questionnaire_type=questionnaire_type,
            session_id=session_id,
            figure_name=figure_name,
        )
        
        return FileResponse(
            path=str(figure_path),
            filename=figure_path.name,
            media_type="image/png",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération figure: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS DE SANTÉ
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Vérifie que l'API est opérationnelle.
    """
    return {"status": "healthy", "service": "questionnaire-analytics-api"}

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Retourne des métriques de service (optionnel).
    """
    import os
    
    # Compter les rapports générés
    reports_count = 0
    for q_type in config.SUPPORTED_QUESTIONNAIRES:
        q_dir = config.REPORTS_DIR / q_type
        if q_dir.exists():
            reports_count += len(list(q_dir.iterdir()))
    
    return {
        "reports_generated": reports_count,
        "supported_questionnaires": config.SUPPORTED_QUESTIONNAIRES,
        "upload_dir_size_mb": round(sum(
            f.stat().st_size for f in config.UPLOAD_DIR.rglob("*") if f.is_file()
        ) / 1024 / 1024, 2),
    }