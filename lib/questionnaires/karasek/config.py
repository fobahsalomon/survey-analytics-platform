# lib/questionnaires/karasek/config.py
from typing import Dict, List

class KarasekConfig:
    # --- Mapping des colonnes (Question -> Code) ---
    RENAME_MAPPING: Dict[str, str] = {
        "Dans mon travail, je dois apprendre des choses nouvelles": "Q1_comp",
        "Dans mon travail j\u2019effectue des t\u00e2ches r\u00e9p\u00e9titives": "Q2_comp",
        # ... (Reprendre tout le mapping du fichier original ici) ...
        # Pour l'exemple, je mets les clés principales
        "Mon travail me demande de travailler tr\u00e8s vite": "Q1_dem",
        "Mon travail me permet souvent de prendre des d\u00e9cisions moi-m\u00eame": "Q1_auto",
        "Mon sup\u00e9rieur se sent concern\u00e9 par le bien-\u00eatre de ses subordonn\u00e9s": "Q1_sup",
        "Les coll\u00e8gues avec qui je travaille sont des gens professionnellement comp\u00e9tent": "Q1_col",
    }

    # --- Items à inverser ---
    INVERT_ITEMS: List[str] = ["Q2_auto", "Q2_comp", "Q4_dem", "Q1_rec", "Q2_rec"]

    # --- Calcul des scores ---
    SCORE_MULTIPLIERS: Dict[str, int] = {
        "comp": 2,
        "auto": 4,
        "dem": 1,
        "sup": 1,
        "col": 1,
    }

    KARASEK_SCORE_COMPOSITION: Dict[str, List[str]] = {
        "Dem_score": ["dem_score"],
        "Lat_score": ["comp_score", "auto_score"],
        "SS_score":  ["sup_score",  "col_score"],
    }

    RH_SCORE_GROUPS: List[str] = ["rec", "equ", "cult", "adq_resources", "adq_role", "sat"]

    # --- SEUILS THÉORIQUES (UNIQUEMENT) ---
    # Basés sur le point médian de l'échelle (2.5 * n_items * multiplier)
    THRESHOLDS: Dict[str, float] = {
        "Dem_score": 22.5,   # 9 items * 2.5
        "Lat_score": 60.0,   # (6*2 + 3*4) * 2.5 normalisé
        "SS_score":  20.0,   # (4 + 4) * 2.5
        "comp_score": 30.0,
        "auto_score": 30.0,
        "sup_score":  10.0,
        "col_score":  10.0,
        "rec_score":  15.0,
        "equ_score":   2.5,
        "cult_score":  5.0,
        "sat_score":   2.5,
    }

    # --- Labels pour les graphiques ---
    SCORE_LABELS: Dict[str, str] = {
        "Dem_score": "Demande psychologique",
        "Lat_score": "Latitude décisionnelle",
        "SS_score":  "Soutien social",
    }
    
    COMPANY_NAME = "Wave-CI" # Ou dynamique via config API