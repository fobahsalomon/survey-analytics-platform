"""
lib/questionnaires/mbi/config.py
Métadonnées du Maslach Burnout Inventory (MBI).
Version adaptée secteur non-clinique (MBI-GS).
Échelle de fréquence : 0 (jamais) → 6 (tous les jours).
"""

LIKERT_MIN = 0
LIKERT_MAX = 6

DIMENSIONS = {
    "exhaustion":    "Épuisement émotionnel",
    "cynicism":      "Cynisme / Dépersonnalisation",
    "efficacy":      "Sentiment d'efficacité personnelle",
}

# Seuils MBI-GS (Schaufeli et al., 1996)
# Épuisement & Cynisme : score élevé = burnout
# Efficacité : score faible = burnout
THRESHOLDS = {
    "exhaustion_score": {"low": 2.0, "high": 3.0},
    "cynicism_score":   {"low": 1.0, "high": 2.0},
    "efficacy_score":   {"low": 3.0, "high": 4.0},   # inversé : faible = problème
}

SCORE_LABELS = {
    "exhaustion_score": "Épuisement émotionnel",
    "cynicism_score":   "Cynisme",
    "efficacy_score":   "Efficacité personnelle",
}

RENAME_MAPPING = {
    # ── Épuisement émotionnel ────────────────────────────────────────────────
    "je me sens émotionnellement vidé(e) par mon travail":                            "Q1_exhaustion",
    "je me sens épuisé(e) à la fin d'une journée de travail":                        "Q2_exhaustion",
    "je me sens fatigué(e) lorsque je me lève le matin et que je dois affronter une nouvelle journée": "Q3_exhaustion",
    "travailler toute la journée est vraiment pénible pour moi":                      "Q4_exhaustion",
    "je me sens brûlé(e) complètement par mon travail":                              "Q5_exhaustion",
    "je me sens frustré(e) par mon travail":                                          "Q6_exhaustion",
    "je pense que je travaille trop dur dans mon emploi":                             "Q7_exhaustion",
    "travailler directement avec des gens me stresse trop":                           "Q8_exhaustion",
    "je me sens au bout du rouleau":                                                  "Q9_exhaustion",
    # ── Cynisme / Dépersonnalisation ─────────────────────────────────────────
    "je traite efficacement les problèmes de mes collègues":                          "Q1_cynicism",
    "je suis devenu(e) indifférent(e) à mon travail":                                 "Q2_cynicism",
    "je suis devenu(e) moins enthousiaste pour mon travail":                          "Q3_cynicism",
    "je doute de la valeur de mon travail":                                           "Q4_cynicism",
    "j'ai du mal à m'identifier à mon travail":                                       "Q5_cynicism",
    # ── Efficacité personnelle ───────────────────────────────────────────────
    "je peux résoudre efficacement les problèmes qui surgissent dans mon travail":    "Q1_efficacy",
    "j'ai l'impression de contribuer de manière positive à l'organisation":           "Q2_efficacy",
    "selon moi, je suis bon(ne) dans mon travail":                                    "Q3_efficacy",
    "je me sens stimulé(e) quand j'atteins mes objectifs":                            "Q4_efficacy",
    "j'ai accompli de nombreuses choses utiles dans mon emploi":                      "Q5_efficacy",
    "dans mon travail, j'ai confiance que je suis efficace pour faire avancer les choses": "Q6_efficacy",
}

# Efficacité est un item positif : score faible = burnout (logique inversée)
INVERT_EFFICACY = False  # on garde la logique de classification inversée dans classify()

MBI_COLORS = {
    "Bas":    "#22C55E",
    "Modéré": "#F97316",
    "Élevé":  "#EF4444",
}

BURNOUT_RISK_LEVELS = {
    "Faible":  "#22C55E",
    "Modéré":  "#F97316",
    "Élevé":   "#EF4444",
}
