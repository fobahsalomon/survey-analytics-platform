# -*- coding: utf-8 -*-
"""
analytics.py — Logique statistique du module Karasek
UNIQUEMENT des calculs. Aucun export, aucune figure ici.
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from . import config as cfg

logger = logging.getLogger(__name__)


# ===========================================================================
# HELPERS INTERNES
# ===========================================================================

def _sort_modalities(series: pd.Series, col_name: str) -> List:
    present = list(series.dropna().unique())
    if col_name in cfg.MODALITY_ORDER:
        ordered  = [m for m in cfg.MODALITY_ORDER[col_name] if m in present]
        ordered += [m for m in present if m not in ordered]
        return ordered
    if set(cfg.SCORE_CAT_ORDER).intersection(present):
        ordered  = [m for m in cfg.SCORE_CAT_ORDER if m in present]
        ordered += [m for m in present if m not in ordered]
        return ordered
    return sorted(present, key=str)


def _imc_category(imc) -> str:
    if pd.isna(imc):  return "Manquant"
    if imc < 18.5:    return "Insuffisance pondérale"
    if imc < 25:      return "Corpulence normale"
    if imc < 30:      return "Surpoids"
    return "Obésité"


# ===========================================================================
# CLEAN DATA  (appelé par questionnaire.py → clean_data)
# ===========================================================================

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline complet de nettoyage :
    1. Renommage des items Likert
    2. Enrichissement socio-démographique (Tranche_age, IMC, Ancienneté)
    3. Nettoyage des valeurs Likert hors plage
    4. Inversion des items cotés négativement
    """
    df = df.copy()

    # 1. Renommage
    mapping = {k: v for k, v in cfg.RENAME_MAPPING.items() if k in df.columns}
    if mapping:
        df = df.rename(columns=mapping)
        logger.info(f"Renommage Likert : {len(mapping)} colonnes")

    # 2. Enrichissement socio-démographique
    df = _enrich_sociodem(df)

    # 3. Nettoyage Likert
    likert_cols = [c for c in df.columns if c.startswith("Q") and "_" in c]
    for col in likert_cols:
        df[col] = _clean_likert(df[col])
    if likert_cols:
        logger.info(f"Nettoyage Likert : {len(likert_cols)} colonnes")

    # 4. Inversion
    df = _invert_items(df)

    return df


def _clean_likert(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    invalid = (~s.between(cfg.LIKERT_MIN, cfg.LIKERT_MAX)) & s.notna()
    if invalid.any():
        logger.warning(
            f"{invalid.sum()} valeurs hors plage "
            f"[{cfg.LIKERT_MIN},{cfg.LIKERT_MAX}] → NaN pour '{series.name}'"
        )
    return s.where(s.between(cfg.LIKERT_MIN, cfg.LIKERT_MAX))


def _invert_items(df: pd.DataFrame) -> pd.DataFrame:
    available = [c for c in cfg.INVERT_ITEMS if c in df.columns]
    missing   = set(cfg.INVERT_ITEMS) - set(available)
    if missing:
        logger.info(f"Items à inverser absents : {missing}")
    if available:
        df[available] = (cfg.LIKERT_MIN + cfg.LIKERT_MAX) - df[available]
        logger.info(f"Inversion appliquée : {available}")
    return df


def _enrich_sociodem(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée les variables dérivées socio-démographiques :
    - Tranche_age / Tranche_age_binaire  (depuis 'Age' numérique)
    - Tranche_anciennete                 (depuis 'Ancienneté' numérique)
    - Categorie_IMC / IMC_binaire        (depuis 'Poids' et 'Taille')
    """
    df = df.copy()

    # Tranche d'âge
    if "Age" in df.columns:
        age_num = pd.to_numeric(df["Age"], errors="coerce")
        df["Tranche_age"] = pd.cut(
            age_num,
            bins=[0, 30, 40, 50, np.inf],
            labels=["20-30 ans", "31-40 ans", "41-50 ans", "51 ans et plus"],
            right=True,
        ).astype(str).replace("nan", np.nan)
        df["Tranche_age"] = df["Tranche_age"].where(df["Tranche_age"] != "nan", np.nan)
        age_bin = pd.Series(np.nan, index=df.index, dtype="object")
        age_bin.loc[age_num <= 40] = "moins de 40 ans"
        age_bin.loc[(age_num > 40) & age_num.notna()] = "plus de 40 ans"
        df["Tranche_age_binaire"] = age_bin
        logger.info("Tranche_age et Tranche_age_binaire créées depuis 'Age'")

    # Ancienneté
    anc_col = "Anciennet\u00e9"
    if anc_col in df.columns:
        anc_num = pd.to_numeric(df[anc_col], errors="coerce")
        df["Tranche_anciennete"] = pd.cut(
            anc_num,
            bins=[-1, 2, 5, 10, 20, np.inf],
            labels=["0-2 ans", "3-5 ans", "6-10 ans", "11-20 ans", "21 ans et +"],
        )
        logger.info("Tranche_anciennete créée")

    # IMC
    if "Poids" in df.columns and "Taille" in df.columns:
        poids  = pd.to_numeric(df["Poids"],  errors="coerce")
        taille = pd.to_numeric(df["Taille"], errors="coerce")
        taille_m = taille / 100 if taille.median() > 3 else taille
        imc_num = poids / (taille_m ** 2)
        df["Categorie_IMC"] = imc_num.apply(_imc_category)
        imc_bin = pd.Series(np.nan, index=df.index, dtype="object")
        is_normal = df["Categorie_IMC"].isin(["Insuffisance pondérale", "Corpulence normale"])
        is_overweight = ~is_normal & (df["Categorie_IMC"] != "Manquant")
        imc_bin.loc[is_normal] = "Normal"
        imc_bin.loc[is_overweight] = "Surpoids/Obésité"
        df["IMC_binaire"] = imc_bin
        logger.info("Categorie_IMC et IMC_binaire créées depuis Poids/Taille")

    return df


# ===========================================================================
# COMPUTE SCORES  (appelé par questionnaire.py → compute_scores)
# ===========================================================================

def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule tous les scores Karasek + RH puis applique
    la classification par médianes et la catégorisation quantiles.
    Retourne un DataFrame enrichi.
    """
    df = df.copy()

    # Scores élémentaires
    for g, mult in cfg.SCORE_MULTIPLIERS.items():
        df[f"{g}_score"] = _compute_group_score(df, g, multiplier=mult)

    # Scores agrégés Karasek
    for name, comps in cfg.KARASEK_SCORE_COMPOSITION.items():
        existing = [c for c in comps if c in df.columns]
        df[name] = sum(df[c] for c in existing) if existing else np.nan

    # Scores RH
    for g in cfg.RH_SCORE_GROUPS:
        df[f"{g}_score"] = _compute_group_score(df, g, multiplier=1)

    logger.info("Scores calculés")

    # Classification Karasek (médianes)
    df = _classify_karasek(df)

    # Catégorisation quantiles
    score_cols = [c for c in cfg.ALL_SCORE_COLS if c in df.columns]
    df = _categorize_scores(df, score_cols)

    return df


def _compute_group_score(df: pd.DataFrame, suffix: str,
                        multiplier: int = 1) -> pd.Series:
    """score = moyenne_items × n_items × multiplier."""
    cols = [c for c in df.columns if c.endswith(f"_{suffix}")]
    if not cols:
        logger.warning(f"Aucun item pour '_{suffix}' → NaN")
        return pd.Series(np.nan, index=df.index, name=f"{suffix}_score")

    n_items    = len(cols)
    n_answered = df[cols].notna().sum(axis=1)
    ssum       = df[cols].sum(axis=1, skipna=True)

    with np.errstate(invalid="ignore", divide="ignore"):
        score = ssum / n_answered.replace(0, np.nan) * n_items * multiplier

    return score.where(n_answered > 0, np.nan).rename(f"{suffix}_score")


def _classify_karasek(df: pd.DataFrame) -> pd.DataFrame:
    """Quadrants, Job strain, Iso strain par médianes internes."""
    required = ["Dem_score", "Lat_score", "SS_score"]
    if any(c not in df.columns for c in required):
        logger.error("Scores manquants pour la classification Karasek")
        return df

    dem_m = df["Dem_score"].median()
    lat_m = df["Lat_score"].median()
    ss_m  = df["SS_score"].median()
    logger.info(f"Médianes → Dem:{dem_m:.2f}  Lat:{lat_m:.2f}  SS:{ss_m:.2f}")

    df["Karasek_quadrant"] = np.select(
        [
            (df["Lat_score"] >= lat_m) & (df["Dem_score"] >= dem_m),
            (df["Lat_score"] >= lat_m) & (df["Dem_score"] <  dem_m),
            (df["Lat_score"] <  lat_m) & (df["Dem_score"] >= dem_m),
        ],
        ["Actif", "Detendu", "Tendu"],
        default="Passif",
    )
    df["Karasek_quadrant_internal"] = df["Karasek_quadrant"]
    df["Job_strain"] = np.where(
        (df["Dem_score"] >= dem_m) & (df["Lat_score"] < lat_m), "Présent", "Absent"
    )
    df["Job_strain_internal"] = df["Job_strain"]
    df["Iso_strain"] = np.where(
        (df["Dem_score"] >= dem_m) & (df["SS_score"] < ss_m), "Présent", "Absent"
    )
    df["Iso_strain_internal"] = df["Iso_strain"]

    df.attrs["thresholds"] = {
        "Dem_median": float(dem_m),
        "Lat_median": float(lat_m),
        "SS_median":  float(ss_m),
    }
    return df


def _categorize_scores(df: pd.DataFrame, score_cols: List[str]) -> pd.DataFrame:
    """Catégorise chaque score en Faible / Moyen / Élevé (quantiles 33/66)."""
    df     = df.copy()
    labels = cfg.CATEGORY_LABELS

    for col in score_cols:
        s = df[col].dropna()
        if s.empty:
            df[f"{col}_quant_cat"] = np.nan
            continue
        q1 = float(s.quantile(cfg.QUANTILE_LOW))
        q2 = float(s.quantile(cfg.QUANTILE_HIGH))
        if q1 >= q2:
            logger.warning(f"Quantiles dégénérés pour {col} → séparation forcée")
            q1 -= 1e-6
            q2 += 1e-6

        def _cat(val, _q1=q1, _q2=q2):
            if pd.isna(val): return "Non renseigné"
            if val <= _q1:   return labels[0]
            if val <= _q2:   return labels[1]
            return labels[2]

        df[f"{col}_quant_cat"] = df[col].apply(_cat)
        df[f"{col}_cat"]       = df[f"{col}_quant_cat"]
        logger.info(f"Catégorisation {col} : q1={q1:.2f}, q2={q2:.2f}")

    return df


# ===========================================================================
# COMPUTE STATISTICS  (appelé par questionnaire.py → compute_statistics)
# ===========================================================================

def compute_descriptives(scores_df: pd.DataFrame) -> pd.DataFrame:
    """
    Statistiques descriptives pour tous les scores numériques.
    Retourne un DataFrame : Variable, Label, N, Moyenne, Écart-type, Min, Max, Médiane, Q1, Q2.
    """
    rows = []
    for col in cfg.ALL_SCORE_COLS:
        if col not in scores_df.columns:
            continue
        s = scores_df[col].dropna()
        rows.append({
            "Variable":    col,
            "Label":       cfg.SCORE_LABELS.get(col, col),
            "N":           len(s),
            "Moyenne":     round(s.mean(), 2),
            "Écart-type":  round(s.std(), 2),
            "Min":         round(s.min(), 2),
            "Max":         round(s.max(), 2),
            "Médiane":     round(s.median(), 2),
            "Q1 (33%)":    round(float(s.quantile(cfg.QUANTILE_LOW)), 2),
            "Q2 (66%)":    round(float(s.quantile(cfg.QUANTILE_HIGH)), 2),
        })
    return pd.DataFrame(rows)


def compute_prevalences(scores_df: pd.DataFrame) -> pd.DataFrame:
    """Prévalences Job strain / Iso strain et répartition des quadrants."""
    rows = []

    if "Karasek_quadrant" in scores_df.columns:
        vc    = scores_df["Karasek_quadrant"].value_counts()
        total = vc.sum()
        for quad in ["Actif", "Detendu", "Tendu", "Passif"]:
            n = vc.get(quad, 0)
            rows.append({
                "Indicateur": "Quadrant Karasek",
                "Modalité":   quad,
                "N":          n,
                "% (total)":  round(n / total * 100, 2) if total else 0,
            })

    for col in ["Job_strain", "Iso_strain"]:
        if col in scores_df.columns:
            n_present = (scores_df[col] == "Présent").sum()
            n_total   = scores_df[col].notna().sum()
            rows.append({
                "Indicateur": col,
                "Modalité":   "Présent",
                "N":          n_present,
                "% (total)":  round(n_present / n_total * 100, 2) if n_total else 0,
            })

    return pd.DataFrame(rows)


# ===========================================================================
# GENERATE CROSSTABS  (appelé par questionnaire.py → generate_crosstabs)
# ===========================================================================

def generate_crosstabs(cleaned_df: pd.DataFrame,
                        scores_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Génère tous les tableaux croisés définis dans config.ALL_CROSSTABS.
    Fusionne cleaned_df et scores_df pour avoir toutes les colonnes disponibles.
    Retourne un dict : clé = 'rv × cv (% par ligne/colonne)' → DataFrame.
    """
    # Fusion : on prend scores_df comme base (il contient cleaned_df + scores)
    df = scores_df.copy()
    # Ajouter les colonnes de cleaned_df absentes de scores_df
    for col in cleaned_df.columns:
        if col not in df.columns:
            df[col] = cleaned_df[col]

    results = {}
    for rv, cv in cfg.ALL_CROSSTABS:
        if rv not in df.columns or cv not in df.columns:
            logger.info(f"Crosstab sauté (colonne absente) : {rv} × {cv}")
            continue
        for by, label in [("row", "% par ligne"), ("col", "% par colonne")]:
            key = f"{rv} × {cv} ({label})"
            results[key] = _build_crosstab(df, rv, cv, by=by)

    logger.info(f"{len(results)} tableaux croisés générés")
    return results


def _build_crosstab(df: pd.DataFrame, row_var: str, col_var: str,
                    by: str = "row", rd: int = 1) -> pd.DataFrame:
    tmp = df[[row_var, col_var]].dropna()
    ct  = pd.crosstab(tmp[row_var], tmp[col_var])

    row_totals  = ct.sum(axis=1)
    col_totals  = ct.sum(axis=0)
    grand_total = int(ct.sum().sum())

    if by == "row":
        ct_pct       = ct.div(row_totals, axis=0) * 100
        total_row_pct = col_totals / grand_total * 100 if grand_total else col_totals * 0
        total_col_pct = pd.Series(100.0, index=ct.index)
    else:
        ct_pct        = ct.div(col_totals, axis=1) * 100
        total_row_pct = pd.Series(100.0, index=ct.columns)
        total_col_pct = row_totals / grand_total * 100 if grand_total else row_totals * 0

    result = pd.DataFrame(index=ct.index, columns=ct.columns, dtype=object)
    for col in ct.columns:
        for idx in ct.index:
            result.at[idx, col] = f"{int(ct.at[idx, col])} ({ct_pct.at[idx, col]:.{rd}f}%)"

    result["Total"] = [
        f"{int(row_totals[i])} ({total_col_pct[i]:.{rd}f}%)" for i in ct.index
    ]
    total_row = {col: f"{int(col_totals[col])} ({total_row_pct[col]:.{rd}f}%)"
                for col in ct.columns}
    total_row["Total"] = f"{grand_total} (100.0%)"
    result.loc["Total"] = pd.Series(total_row)

    return result

