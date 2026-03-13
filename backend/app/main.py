# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from core.config import config
from core.logger import logger
from api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application.
    """
    # Startup
    logger.info("Démarrage de l'API Questionnaire Analytics...")
    config.init_dirs()
    logger.info(f" Upload Dir: {config.UPLOAD_DIR}")
    logger.info(f" Reports Dir: {config.REPORTS_DIR}")
    
    yield
    
    # Shutdown
    logger.info(" Arrêt de l'API...")

# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION FASTAPI
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Questionnaire Analytics Platform",
    description="API pour l'analyse automatique de questionnaires RH (Karasek, QVT, MBI)",
    version="1.0.0",
    lifespan=lifespan,
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

app.include_router(router)

# ─────────────────────────────────────────────────────────────────────────────
# ROOT ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "message": "Questionnaire Analytics API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }

# ─────────────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
    )