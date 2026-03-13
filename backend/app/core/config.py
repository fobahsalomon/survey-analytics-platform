# backend/core/config.py
import os
from pathlib import Path
from typing import Dict, List

class Config:
    # ── Chemins ────────────────────────────────────────────────────────────
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_DIR = BASE_DIR / "uploads"
    REPORTS_DIR = BASE_DIR / "reports"
    FIGURES_DIR = BASE_DIR / "reports" / "figures"
    
    # ── Serveur ────────────────────────────────────────────────────────────
    HOST = os.getenv("API_HOST", "0.0.0.0")
    PORT = int(os.getenv("API_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # ── Questionnaires supportés ───────────────────────────────────────────
    SUPPORTED_QUESTIONNAIRES: List[str] = ["karasek", "qvt", "mbi"]
    
    # ── Limites ────────────────────────────────────────────────────────────
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS = {"csv"}
    
    # ── CORS ───────────────────────────────────────────────────────────────
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    @classmethod
    def init_dirs(cls):
        """Crée les répertoires nécessaires au démarrage"""
        for d in [cls.UPLOAD_DIR, cls.REPORTS_DIR, cls.FIGURES_DIR]:
            d.mkdir(parents=True, exist_ok=True)

config = Config()