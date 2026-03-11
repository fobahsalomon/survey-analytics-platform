# =============================================================================
# FONCTIONS DE NETTOYAGE COMMUNES À TOUS LES QUESTIONNAIRES
# =============================================================================
"""
Contient toutes les fonctions de prétraitement partagées:
- Catégorisation âge, ancienneté, IMC
- Nettoyage Likert
- Gestion des manquants
"""

import pandas as pd
import numpy as np


# -----------------------------------------------------------------------------
# CATÉGORISATION SOCIO-DÉMOGRAPHIQUE
# -----------------------------------------------------------------------------

def categorize_age(age_value):
    """
    Catégorise l'âge en tranches prédéfinies.
    
    Parameters
    ----------
    age_value : int/float
        Âge en années
        
    Returns
    -------
    str
        Tranche d'âge
    """
    if pd.isna(age_value):
        return "Non renseigné"
    try:
        age = int(age_value)
    except (ValueError, TypeError):
        return "Non renseigné"
    
    if 16 <= age <= 24:
        return '16-24 ans'
    elif 25 <= age <= 34:
        return '25-34 ans'
    elif 35 <= age <= 44:
        return '35-44 ans'
    elif 45 <= age <= 54:
        return '45-54 ans'
    elif 55 <= age <= 65:
        return '55-65 ans'
    else:
        return 'Autre'


def categorize_seniority(seniority_value):
    """
    Catégorise l'ancienneté en tranches prédéfinies.
    
    Parameters
    ----------
    seniority_value : int/float
        Ancienneté en années
        
    Returns
    -------
    str
        Tranche d'ancienneté
    """
    if pd.isna(seniority_value):
        return "Non renseigné"
    try:
        seniority = float(seniority_value)
    except (ValueError, TypeError):
        return "Non renseigné"
    
    if seniority < 0:
        return "Non renseigné"
    elif 0 <= seniority <= 2:
        return '0-2 ans'
    elif 3 <= seniority <= 5:
        return '3-5 ans'
    elif 6 <= seniority <= 10:
        return '6-10 ans'
    elif 11 <= seniority <= 20:
        return '11-20 ans'
    elif seniority >= 21:
        return '21 ans et +'
    else:
        return "Non renseigné"


def calculate_imc(row):
    """
    Calcule l'IMC à partir du poids et de la taille.
    
    Parameters
    ----------
    row : pd.Series
        Ligne du DataFrame avec 'Poids' et 'Taille'
        
    Returns
    -------
    float
        IMC calculé ou NaN
    """
    try:
        poids = row.get("Poids")
        taille = row.get("Taille")
        
        if pd.isna(poids) or pd.isna(taille) or taille <= 0:
            return np.nan
        
        imc = poids / (taille / 100) ** 2
        return round(imc, 1)
    except (TypeError, ValueError, ZeroDivisionError):
        return np.nan


def categorize_imc(imc_value):
    """
    Catégorise l'IMC selon les standards OMS.
    
    Parameters
    ----------
    imc_value : float
        Valeur de l'IMC
        
    Returns
    -------
    str
        Catégorie d'IMC
    """
    if pd.isna(imc_value):
        return "Manquant"
    
    if imc_value < 18.5:
        return "Insuffisance ponderale"
    elif imc_value < 25:
        return "Corpulence normale"
    elif imc_value < 30:
        return "Surpoids"
    else:
        return "Obesite"


# -----------------------------------------------------------------------------
# NETTOYAGE GÉNÉRAL
# -----------------------------------------------------------------------------

def clean_categorical_columns(df, fill_value="Non renseigné"):
    """
    Remplit les valeurs manquantes des colonnes texte.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame à nettoyer
    fill_value : str
        Valeur de remplissage
        
    Returns
    -------
    pd.DataFrame
        DataFrame nettoyé
    """
    df = df.copy()
    cat_cols = df.select_dtypes(include="object").columns
    df[cat_cols] = df[cat_cols].fillna(fill_value)
    return df


def clean_likert_series(series, min_val=1, max_val=4):
    """
    Nettoie une série Likert pour qu'elle soit entre min_val et max_val.
    
    Parameters
    ----------
    series : pd.Series
        Série de valeurs Likert
    min_val : int
        Valeur minimum valide
    max_val : int
        Valeur maximum valide
        
    Returns
    -------
    pd.Series
        Série nettoyée
    """
    series = pd.to_numeric(series, errors="coerce")
    return series.where(series.between(min_val, max_val))


def clean_likert_columns(df, columns, min_val=1, max_val=4):
    """
    Nettoie plusieurs colonnes Likert.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame contenant les colonnes Likert
    columns : list
        Liste des noms de colonnes à nettoyer
    min_val : int
        Valeur minimum valide
    max_val : int
        Valeur maximum valide
        
    Returns
    -------
    pd.DataFrame
        DataFrame avec colonnes nettoyées
    """
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = clean_likert_series(df[col], min_val, max_val)
    return df


def invert_Likert_items(df, columns, min_val=1, max_val=4):
    """
    Inverse les items Likert pour aligner la direction des scores.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame contenant les colonnes à inverser
    columns : list
        Liste des noms de colonnes à inverser
    min_val : int
        Minimum de l'échelle
    max_val : int
        Maximum de l'échelle
        
    Returns
    -------
    pd.DataFrame
        DataFrame avec colonnes inversées
    """
    df = df.copy()
    existing_cols = [c for c in columns if c in df.columns]
    if existing_cols:
        df[existing_cols] = (min_val + max_val) - df[existing_cols]
    return df


def compute_score_sum(df, columns, multiplier=1):
    """
    Calcule la somme d'une liste de colonnes avec multiplicateur.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame contenant les colonnes
    columns : list
        Liste des noms de colonnes à sommer
    multiplier : float
        Multiplicateur à appliquer au score final
        
    Returns
    -------
    pd.Series
        Score calculé
    """
    existing_cols = [c for c in columns if c in df.columns]
    if not existing_cols:
        return pd.Series(0, index=df.index)
    return df[existing_cols].sum(axis=1) * multiplier