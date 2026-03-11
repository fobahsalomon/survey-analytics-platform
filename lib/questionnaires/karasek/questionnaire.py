# -*- coding: utf-8 -*-
"""
questionnaire.py — Classe principale du module Karasek
Respecte STRICTEMENT l'interface définie par BaseQuestionnaire.
"""

import logging

import pandas as pd

from common.base_questionnaire import BaseQuestionnaire
from . import analytics
from . import reporting

logger = logging.getLogger(__name__)


class KarasekQuestionnaire(BaseQuestionnaire):
    """
    Analyse complète du questionnaire Karasek (RPS).

    Paramètres
    ----------
    df : pd.DataFrame
        Données brutes chargées depuis le CSV.
    company_name : str, optional
        Nom de l'entreprise affiché dans les titres des graphiques
        et les rapports. Défaut : "Entreprise".

    Exemple d'utilisation
    ---------------------
    >>> import pandas as pd
    >>> from questionnaires.karasek.questionnaire import KarasekQuestionnaire
    >>>
    >>> df = pd.read_csv("data/Karasek_Wave-CI.csv", sep=None, engine="python")
    >>> q = KarasekQuestionnaire(df, company_name="Wave-CI")
    >>> q.run_full_analysis("results/karasek")
    """

    def __init__(self, df: pd.DataFrame, company_name: str = "Entreprise"):
        super().__init__(df)

        # ── Option entreprise ─────────────────────────────────────────
        self.company_name: str = company_name

        # ── Attributs de résultats ────────────────────────────────────
        self.scores_df:    pd.DataFrame | None = None
        self.descriptives: pd.DataFrame | None = None
        self.prevalences:  pd.DataFrame | None = None
        self.crosstabs:    dict         | None = None
        self.metrics:      dict                = {}

    # ------------------------------------------------------------------
    # INTERFACE PUBLIQUE OBLIGATOIRE
    # ------------------------------------------------------------------

    def clean_data(self) -> None:
        """
        Étape 1 — Nettoyage et enrichissement.
        - Appelle clean_common_variables() de BaseQuestionnaire
        (nettoyage des variables communes à tous les questionnaires)
        - Puis pipeline Karasek : renommage Likert, socio-dem, inversion
        """
        self.clean_common_variables()                        # BaseQuestionnaire
        self.cleaned_df = analytics.clean_data(self.raw_df) # pipeline Karasek
        logger.info(
            f"[Karasek – {self.company_name}] "
            f"clean_data OK — {self.cleaned_df.shape[0]} lignes, "
            f"{self.cleaned_df.shape[1]} colonnes"
        )

        # Suppression des lignes avec NA sur les items Likert
        likert_cols = [c for c in self.cleaned_df.columns
                    if c.startswith("Q") and "_" in c]
        if likert_cols:
            before = len(self.cleaned_df)
            self.cleaned_df = self.cleaned_df.dropna(subset=likert_cols)
            dropped = before - len(self.cleaned_df)
            if dropped:
                logger.info(f"Lignes supprimées (NA Likert) : {dropped}")

        self.metrics["rows_initial"] = len(self.raw_df)
        self.metrics["rows_final"]   = len(self.cleaned_df)

    def compute_scores(self) -> None:
        """
        Étape 2 — Calcul de tous les scores Karasek et RH
        + classification par médianes + catégorisation quantiles.
        """
        if self.cleaned_df is None:
            raise RuntimeError("Appelez clean_data() avant compute_scores().")

        self.scores_df = analytics.compute_scores(self.cleaned_df)

        # Récupération des seuils stockés dans les attrs du DataFrame
        self.metrics["thresholds"] = self.scores_df.attrs.get("thresholds", {})

        logger.info(
            f"[Karasek – {self.company_name}] "
            f"compute_scores OK — {self.scores_df.shape[1]} colonnes au total"
        )

    def compute_statistics(self) -> None:
        """
        Étape 3 — Statistiques descriptives + prévalences RPS.
        Remplit self.descriptives et self.prevalences.
        """
        if self.scores_df is None:
            raise RuntimeError("Appelez compute_scores() avant compute_statistics().")

        self.descriptives = analytics.compute_descriptives(self.scores_df)
        self.prevalences  = analytics.compute_prevalences(self.scores_df)

        logger.info(
            f"[Karasek – {self.company_name}] "
            f"compute_statistics OK — {len(self.descriptives)} scores décrits"
        )

    def generate_crosstabs(self) -> None:
        """
        Étape 4 — Tableaux croisés définis dans config.ALL_CROSSTABS.
        Remplit self.crosstabs (dict clé → DataFrame).
        """
        if self.cleaned_df is None or self.scores_df is None:
            raise RuntimeError(
                "Appelez clean_data() et compute_scores() avant generate_crosstabs()."
            )

        self.crosstabs = analytics.generate_crosstabs(
            self.cleaned_df, self.scores_df
        )
        logger.info(
            f"[Karasek – {self.company_name}] "
            f"generate_crosstabs OK — {len(self.crosstabs)} tableaux"
        )

    def export_excel(self, output_path: str) -> None:
        """Étape 5 — Export Excel structuré dans output_path/."""
        reporting.export_excel(self, output_path)

    def export_figures(self, output_path: str) -> None:
        """Étape 6 — Export de toutes les figures dans output_path/figures/."""
        reporting.export_figures(self, output_path)

    def export_word(self, output_path: str) -> None:
        """Étape 7 — Export du rapport Word dans output_path/."""
        reporting.export_word(self, output_path)

    def run_full_analysis(self, output_path: str) -> None:
        """
        Lance le pipeline complet dans l'ordre obligatoire.

        Paramètres
        ----------
        output_path : str
            Dossier de destination des résultats.
            Exemple : "results/karasek"
        """
        print(f"\n{'='*60}")
        print(f"  Analyse Karasek — {self.company_name}")
        print(f"{'='*60}")

        print("  [1/7] Nettoyage des données...")
        self.clean_data()

        print("  [2/7] Calcul des scores...")
        self.compute_scores()

        print("  [3/7] Statistiques descriptives...")
        self.compute_statistics()

        print("  [4/7] Tableaux croisés...")
        self.generate_crosstabs()

        print("  [5/7] Export Excel...")
        self.export_excel(output_path)

        print("  [6/7] Export figures...")
        self.export_figures(output_path)

        print("  [7/7] Export Word...")
        self.export_word(output_path)

        print(f"\n✅ Analyse terminée — résultats dans : {output_path}")
        print(f"   Lignes : {self.metrics.get('rows_final', '?')} / "
            f"{self.metrics.get('rows_initial', '?')}")
        print(f"{'='*60}\n")
