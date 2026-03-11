# =============================================================================
# CLASSE DE BASE POUR TOUS LES QUESTIONNAIRES
# =============================================================================
"""
Interface commune que tous les questionnaires doivent implémenter.
Contient la logique partagée (nettoyage socio-démographique, etc.)
"""

import pandas as pd
import numpy as np
import os
from abc import ABC, abstractmethod
from common.common_cleaning import \
    categorize_age, categorize_seniority, calculate_imc,\
    categorize_imc, clean_categorical_columns

from common.file_utils import ensure_directory


class BaseQuestionnaire(ABC):
    """
    Classe abstraite de base pour tous les questionnaires.
    
    Attributs standardisés:
    - raw_df: Données brutes chargées
    - cleaned_df: Données après nettoyage
    - scores_df: Données avec scores calculés
    - descriptives: Statistiques descriptives
    - crosstabs: Tableaux croisés
    - test_results: Résultats de tests statistiques
    """

    def __init__(self, df):
        """
        Initialise le questionnaire avec les données brutes.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame brut contenant les réponses
        """
        self.raw_df = df.copy()
        self.cleaned_df = None
        self.scores_df = None
        self.descriptives = None
        self.crosstabs = None
        self.test_results = None
        self.figures_generated = []
        self.excel_sheets = {}

    # =========================================================================
    # MÉTHODES ABSTRAITES (À IMPLÉMENTER DANS CHAQUE QUESTIONNAIRE)
    # =========================================================================

    @abstractmethod
    def clean_data(self):
        """Nettoie les données spécifiques au questionnaire."""
        pass

    @abstractmethod
    def compute_scores(self):
        """Calcule les scores spécifiques au questionnaire."""
        pass

    @abstractmethod
    def compute_statistics(self):
        """Calcule les statistiques descriptives."""
        pass

    @abstractmethod
    def generate_crosstabs(self):
        """Génère les tableaux croisés spécifiques."""
        pass

    @abstractmethod
    def export_excel(self, output_path):
        """Exporte les résultats vers Excel."""
        pass

    @abstractmethod
    def export_figures(self, output_path):
        """Génère et exporte les figures."""
        pass

    @abstractmethod
    def export_word(self, output_path):
        """Exporte le rapport vers Word."""
        pass

    # =========================================================================
    # MÉTHODES COMMUNES (PARTAGÉES PAR TOUS LES QUESTIONNAIRES)
    # =========================================================================

    def clean_common_variables(self):
        """
        Nettoie les variables socio-démographiques communes à tous les questionnaires.
        
        Crée:
        - Tranche_age
        - Tranche_anciennete
        - IMC, Categorie_IMC, IMC_binaire
        - Gestion des NA pour colonnes texte
        """
        df = self.cleaned_df.copy() if self.cleaned_df is not None else self.raw_df.copy()
        
        # 1. Gestion des valeurs manquantes texte
        df = clean_categorical_columns(df)
        
        # 2. Tranches d'âge
        if "Age" in df.columns:
            df["Tranche_age"] = df["Age"].apply(categorize_age)
        
        # 3. Calcul et catégorisation IMC
        if {"Poids", "Taille"}.issubset(df.columns):
            df["IMC"] = df.apply(calculate_imc, axis=1)
            df["Categorie_IMC"] = df["IMC"].apply(categorize_imc)
            df["IMC_binaire"] = df["Categorie_IMC"].apply(
                lambda x: "Normal/Insuffisance" if x in ["Insuffisance ponderale", "Corpulence normale"] 
                else "Excès pondéral" if x in ["Surpoids", "Obesite"] else "Manquant"
            )
        
        # 4. Ancienneté
        if "Ancienneté" in df.columns:
            df["Tranche_anciennete"] = df["Ancienneté"].apply(categorize_seniority)
        
        self.cleaned_df = df
        return df

    def get_sample_description(self):
        """
        Génère la description de l'échantillon.
        
        Returns
        -------
        dict
            Dictionnaire avec N total et effectifs par variable
        """
        if self.cleaned_df is None:
            return {}
        
        description = {
            "N_total": len(self.cleaned_df),
            "variables": {}
        }
        
        demo_vars = ["Tranche_age", "Genre", "Tranche_anciennete", "Categorie_IMC"]
        for var in demo_vars:
            if var in self.cleaned_df.columns:
                description["variables"][var] = self.cleaned_df[var].value_counts().to_dict()
        
        return description

    def run_full_analysis(self, output_path):
        """
        Exécute le pipeline complet d'analyse.
        
        Parameters
        ----------
        output_path : str
            Chemin du répertoire de sortie
        """
        ensure_directory(output_path)
        
        print(f"🚀 Démarrage de l'analyse complète...")
        print(f"📁 Répertoire de sortie: {output_path}")
        
        # Étape 1: Nettoyage
        print("\n📋 Étape 1/6: Nettoyage des données...")
        self.clean_data()
        print(f"   ✅ Données nettoyées: {len(self.cleaned_df)} répondants")
        
        # Étape 2: Scores
        print("\n📊 Étape 2/6: Calcul des scores...")
        self.compute_scores()
        print(f"   ✅ Scores calculés: {self.scores_df.shape[1]} colonnes")
        
        # Étape 3: Statistiques
        print("\n📈 Étape 3/6: Statistiques descriptives...")
        self.compute_statistics()
        print(f"   ✅ Statistiques générées")
        
        # Étape 4: Tableaux croisés
        print("\n🔀 Étape 4/6: Tableaux croisés...")
        self.generate_crosstabs()
        print(f"   ✅ Tableaux générés")
        
        # Étape 5: Excel
        print("\n📁 Étape 5/6: Export Excel...")
        excel_path = os.path.join(output_path, "results.xlsx")
        self.export_excel(excel_path)
        print(f"   ✅ Excel exporté: {excel_path}")
        
        # Étape 6: Figures
        print("\n📊 Étape 6/6: Génération des figures...")
        figures_path = os.path.join(output_path, "figures")
        self.export_figures(figures_path)
        print(f"   ✅ Figures générées: {len(self.figures_generated)} graphiques")
        
        # Étape 7: Word
        print("\n📄 Export Word...")
        word_path = os.path.join(output_path, "rapport.docx")
        self.export_word(word_path)
        print(f"   ✅ Rapport généré: {word_path}")
        
        print("\n" + "="*60)
        print("✅ ANALYSE TERMINÉE AVEC SUCCÈS")
        print("="*60)

    def get_summary(self):
        """
        Retourne un résumé de l'analyse.
        
        Returns
        -------
        dict
            Résumé avec nombres de lignes, colonnes, figures, etc.
        """
        return {
            "n_respondents": len(self.cleaned_df) if self.cleaned_df is not None else 0,
            "n_variables": len(self.cleaned_df.columns) if self.cleaned_df is not None else 0,
            "n_scores": len(self.scores_df.columns) if self.scores_df is not None else 0,
            "n_figures": len(self.figures_generated),
            "n_crosstabs": len(self.crosstabs) if self.crosstabs is not None else 0,
        }