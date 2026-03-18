"""
lib/questionnaires/karasek/questionnaire.py
Pipeline principal du questionnaire Karasek (DCS).
"""

import re
import numpy as np
import pandas as pd

from lib.common import (
    BaseQuestionnaire, clean_pii, enrich_sociodem,
    clip_likert, invert_items, compute_group_score,
    normalize_text,
)
from lib.common.common_cleaning import remap_age_tranche

from .config import (
    LIKERT_MIN, LIKERT_MAX, THRESHOLDS,
    RENAME_MAPPING, INVERT_ITEMS, SCORE_MULTIPLIERS, RH_SCORE_GROUPS,
)


ITEM_PATTERN = re.compile(
    r"Q\d+_(comp|auto|dem|sup|col|rec|equ|cult|adq_resources|adq_role|sat)$"
)


def _fuzzy_rename(df: pd.DataFrame) -> pd.DataFrame:
    """Renomme les colonnes questions → codes Q via matching normalisé."""
    norm_map = {normalize_text(k): v for k, v in RENAME_MAPPING.items()}
    rename = {}
    for col in df.columns:
        nc = normalize_text(col)
        if nc in norm_map:
            rename[col] = norm_map[nc]
    return df.rename(columns=rename) if rename else df


class KarasekQuestionnaire(BaseQuestionnaire):
    """
    Implémente le pipeline complet du modèle Karasek Demande-Contrôle-Soutien.
    Utilise uniquement les seuils théoriques (point médian de l'échelle Likert 1-4).
    """

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        # Cette étape prépare le fichier avant tout calcul :
        # suppression de colonnes sensibles, enrichissement socio-démo,
        # harmonisation éventuelle des tranches d'âge.
        df, _ = clean_pii(df)
        df = enrich_sociodem(df)
        if "Tranche d’âge" in df.columns:
            df = remap_age_tranche(df, "Tranche d’âge")
        return df

    def score(self, df: pd.DataFrame) -> pd.DataFrame:
        df_out = df.copy()

        # 1. Renommage des colonnes questions
        # On essaye de faire correspondre les libellés du fichier source aux
        # codes internes attendus par le moteur (`Q1_dem`, `Q2_auto`, etc.).
        df_out = _fuzzy_rename(df_out)

        # 2. Nettoyage Likert
        # Toutes les réponses sont converties en valeurs numériques propres.
        lk_cols = [c for c in df_out.columns if ITEM_PATTERN.match(c)]
        for col in lk_cols:
            df_out[col] = clip_likert(df_out[col], LIKERT_MIN, LIKERT_MAX)

        # 3. Inversion des items négatifs
        # Certaines questions sont formulées à l'envers et doivent être
        # inversées pour que le sens du score reste cohérent.
        df_out = invert_items(df_out, INVERT_ITEMS, LIKERT_MIN, LIKERT_MAX)

        # 4. Scores Karasek principaux
        # On calcule les briques de base du modèle avant les scores composites.
        for g, mult in SCORE_MULTIPLIERS.items():
            col_name = f"{g}_score"
            computed = compute_group_score(df_out, g, multiplier=mult)
            if computed.notna().any():
                df_out[col_name] = computed
            elif col_name not in df_out.columns:
                df_out[col_name] = np.nan

        # 5. Scores composites
        # Ces scores résument plusieurs sous-dimensions en indicateurs métiers
        # plus directement interprétables dans le dashboard et le rapport.
        comp_cols = [c for c in ["comp_score", "auto_score"] if c in df_out.columns]
        ss_cols = [c for c in ["sup_score", "col_score"] if c in df_out.columns]

        if "Lat_score" not in df_out.columns or df_out["Lat_score"].isna().all():
            df_out["Lat_score"] = sum(df_out[c] for c in comp_cols) if comp_cols else np.nan

        if "Dem_score" not in df_out.columns or df_out["Dem_score"].isna().all():
            df_out["Dem_score"] = df_out.get("dem_score", pd.Series(np.nan, index=df_out.index))

        if "SS_score" not in df_out.columns or df_out["SS_score"].isna().all():
            df_out["SS_score"] = sum(df_out[c] for c in ss_cols) if ss_cols else np.nan

        # 6. Scores RH
        # Ces scores supplémentaires enrichissent la lecture du climat
        # organisationnel autour du noyau Karasek.
        for g in RH_SCORE_GROUPS:
            col_name = f"{g}_score"
            computed = compute_group_score(df_out, g, multiplier=1)
            if computed.notna().any():
                df_out[col_name] = computed
            elif col_name not in df_out.columns:
                df_out[col_name] = np.nan

        return df_out

    def classify(self, df: pd.DataFrame) -> pd.DataFrame:
        df_out = df.copy()
        req = ["Dem_score", "Lat_score", "SS_score"]
        if any(c not in df_out.columns for c in req):
            return df_out

        DT = THRESHOLDS["Dem_score"]
        LT = THRESHOLDS["Lat_score"]
        ST = THRESHOLDS["SS_score"]

        df_out["Karasek_quadrant_theoretical"] = np.select(
            [
                (df_out["Lat_score"] >= LT) & (df_out["Dem_score"] >= DT),
                (df_out["Lat_score"] >= LT) & (df_out["Dem_score"] < DT),
                (df_out["Lat_score"] < LT)  & (df_out["Dem_score"] >= DT),
            ],
            ["Actif", "Detendu", "Tendu"],
            default="Passif",
        )

        df_out["Job_strain_theoretical"] = np.where(
            (df_out["Dem_score"] >= DT) & (df_out["Lat_score"] < LT), "Présent", "Absent"
        )
        df_out["Iso_strain_theoretical"] = np.where(
            (df_out["Dem_score"] >= DT) & (df_out["SS_score"] < ST), "Présent", "Absent"
        )

        # Catégories haute/faible pour chaque score
        for col, thresh in THRESHOLDS.items():
            if col in df_out.columns:
                df_out[f"{col}_theo_cat"] = np.where(
                    df_out[col].isna(), "Non renseigné",
                    np.where(df_out[col] <= thresh, "Faible", "Élevé"),
                )

        return df_out

    def analytics(self, df: pd.DataFrame) -> dict:
        """Calcule les indicateurs agrégés pour le dashboard."""
        from .analytics import KarasekAnalytics
        return KarasekAnalytics(df).compute()

    def count_items(self, df: pd.DataFrame) -> int:
        """Nombre d'items Likert Karasek détectés dans le DataFrame."""
        return sum(1 for c in df.columns if ITEM_PATTERN.match(c))
