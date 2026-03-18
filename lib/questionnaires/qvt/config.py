"""
lib/questionnaires/qvt/config.py
Métadonnées du questionnaire Qualité de Vie au Travail (QVT).
Basé sur les dimensions ANACT / accord national interprofessionnel 2013.
"""

LIKERT_MIN = 1
LIKERT_MAX = 5

DIMENSIONS = {
    "relations":     "Relations au travail",
    "contenu":       "Contenu & sens du travail",
    "environnement": "Environnement & conditions",
    "organisation":  "Organisation du travail",
    "developpement": "Développement professionnel",
    "equilibre":     "Équilibre vie pro/perso",
}

THRESHOLDS = {
    "relations_score":      15.0,
    "contenu_score":        12.0,
    "environnement_score":  12.0,
    "organisation_score":   12.0,
    "developpement_score":   9.0,
    "equilibre_score":      12.0,
    "qvt_global_score":     72.0,
}

SCORE_LABELS = {
    "relations_score":      "Relations au travail",
    "contenu_score":        "Contenu & sens du travail",
    "environnement_score":  "Environnement & conditions",
    "organisation_score":   "Organisation du travail",
    "developpement_score":  "Développement professionnel",
    "equilibre_score":      "Équilibre vie pro/perso",
    "qvt_global_score":     "Score QVT global",
}

# Mapping libellé → code item
RENAME_MAPPING = {
    # ── Relations au travail ────────────────────────────────────────────────
    "les relations avec mes collègues sont bonnes":                                   "Q1_relations",
    "je me sens respecté(e) par mes collègues":                                       "Q2_relations",
    "je peux compter sur l'aide de mon manager en cas de difficulté":                 "Q3_relations",
    "les conflits sont gérés de manière constructive":                                "Q4_relations",
    # ── Contenu & sens ──────────────────────────────────────────────────────
    "mon travail a du sens pour moi":                                                 "Q1_contenu",
    "j'ai suffisamment d'autonomie dans la réalisation de mes tâches":                "Q2_contenu",
    "mon travail me permet d'utiliser mes compétences":                               "Q3_contenu",
    # ── Environnement & conditions ───────────────────────────────────────────
    "mon environnement de travail est agréable et fonctionnel":                       "Q1_environnement",
    "je dispose des outils nécessaires pour bien travailler":                         "Q2_environnement",
    "mon espace de travail me permet de me concentrer":                               "Q3_environnement",
    # ── Organisation du travail ──────────────────────────────────────────────
    "ma charge de travail est raisonnable":                                           "Q1_organisation",
    "les priorités sont clairement définies":                                         "Q2_organisation",
    "les processus et procédures facilitent mon travail":                             "Q3_organisation",
    # ── Développement professionnel ──────────────────────────────────────────
    "j'ai des perspectives d'évolution dans mon organisation":                        "Q1_developpement",
    "les formations proposées correspondent à mes besoins":                           "Q2_developpement",
    # ── Équilibre vie pro/perso ───────────────────────────────────────────────
    "je parviens à concilier vie professionnelle et personnelle":                     "Q1_equilibre",
    "mes horaires de travail me conviennent":                                         "Q2_equilibre",
    "le télétravail / la flexibilité horaire est suffisant(e)":                       "Q3_equilibre",
}

INVERT_ITEMS = []  # Tous les items QVT sont formulés positivement

QVT_COLORS = {
    "Satisfaisant":    "#22C55E",
    "Mitigé":          "#F97316",
    "Insatisfaisant":  "#EF4444",
}
