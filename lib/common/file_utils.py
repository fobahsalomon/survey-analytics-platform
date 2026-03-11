# =============================================================================
# UTILITAIRES DE GESTION DE FICHIERS
# =============================================================================
"""
Fonctions utilitaires pour la gestion des répertoires et fichiers.
"""

import os
import pandas as pd
from pathlib import Path


def ensure_directory(path):
    """
    Crée un répertoire s'il n'existe pas.
    
    Parameters
    ----------
    path : str
        Chemin du répertoire à créer
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_safe_filename(name, extension=".png"):
    """
    Génère un nom de fichier sécurisé (sans caractères spéciaux).
    
    Parameters
    ----------
    name : str
        Nom de base
    extension : str
        Extension du fichier
        
    Returns
    -------
    str
        Nom de fichier sécurisé
    """
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in str(name))
    return f"{safe_name}{extension}"


def save_dataframe_to_excel(df, writer, sheet_name, max_rows=1000000):
    """
    Sauvegarde un DataFrame dans un fichier Excel avec gestion des erreurs.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame à sauvegarder
    writer : pd.ExcelWriter
        Writer Excel
    sheet_name : str
        Nom de l'onglet
    max_rows : int
        Nombre maximum de lignes par onglet Excel
    """
    try:
        # Tronquer si nécessaire (limitation Excel)
        if len(df) > max_rows:
            df = df.head(max_rows)
        
        # Nettoyer les noms de colonnes pour Excel
        df_clean = df.copy()
        df_clean.columns = [str(c)[:31] for c in df_clean.columns]  # Max 31 caractères
        
        df_clean.to_excel(writer, sheet_name=sheet_name[:31], index=True)
    except Exception as e:
        print(f"⚠️ Erreur lors de l'export de l'onglet '{sheet_name}': {e}")


def list_files_in_directory(directory, extension=None):
    """
    Liste les fichiers dans un répertoire.
    
    Parameters
    ----------
    directory : str
        Chemin du répertoire
    extension : str, optional
        Filtre par extension (ex: ".png")
        
    Returns
    -------
    list
        Liste des chemins de fichiers
    """
    files = []
    if os.path.exists(directory):
        for f in os.listdir(directory):
            if extension is None or f.endswith(extension):
                files.append(os.path.join(directory, f))
    return files