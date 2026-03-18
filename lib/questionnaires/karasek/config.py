"""
lib/questionnaires/karasek/config.py
Métadonnées, mappings et seuils du modèle Karasek Demande-Contrôle-Soutien.
"""

LIKERT_MIN = 1
LIKERT_MAX = 4

# Seuils théoriques — point médian de l'échelle Likert 1-4 (non cliniques)
THRESHOLDS = {
    "Dem_score":           22.5,
    "Lat_score":           60.0,
    "SS_score":            20.0,
    "comp_score":          30.0,
    "auto_score":          30.0,
    "sup_score":           10.0,
    "col_score":           10.0,
    "rec_score":           15.0,
    "equ_score":            2.5,
    "cult_score":           5.0,
    "sat_score":            2.5,
    "adq_resources_score":  5.0,
    "adq_role_score":       5.0,
}

SCORE_LABELS = {
    "Dem_score":           "Demande psychologique",
    "Lat_score":           "Latitude décisionnelle",
    "SS_score":            "Soutien social",
    "comp_score":          "Utilisation des compétences",
    "auto_score":          "Autonomie décisionnelle",
    "sup_score":           "Soutien hiérarchique",
    "col_score":           "Soutien des collègues",
    "rec_score":           "Reconnaissance",
    "equ_score":           "Équité de charge",
    "cult_score":          "Culture d'entreprise",
    "sat_score":           "Satisfaction",
    "adq_resources_score": "Ressources & Objectifs",
    "adq_role_score":      "Adéquation formation/rôle",
}

KARASEK_COLORS = {
    "Actif":   "#22C55E",
    "Détendu": "#38A3E8",
    "Detendu": "#38A3E8",
    "Tendu":   "#EF4444",
    "Passif":  "#94A3B8",
}

# Items à inverser avant le scoring
INVERT_ITEMS = ["Q2_auto", "Q2_comp", "Q4_dem", "Q1_rec", "Q2_rec"]

# Multiplicateurs pour chaque dimension
SCORE_MULTIPLIERS = {"comp": 2, "auto": 4, "dem": 1, "sup": 1, "col": 1}

# Groupes de scores RH
RH_SCORE_GROUPS = ["rec", "equ", "cult", "adq_resources", "adq_role", "sat"]

# Mapping libellé complet → code Q
RENAME_MAPPING = {
    # ── Utilisation des compétences (comp) ──────────────────────────────────
    "dans mon travail, je dois apprendre des choses nouvelles":                                                              "Q1_comp",
    "dans mon travail j'effectue des tâches répétitives":                                                                    "Q2_comp",
    "mon travail me demande d'être créatif":                                                                                  "Q3_comp",
    "mon travail me demande un haut niveau de compétence":                                                                    "Q4_comp",
    "dans mon travail, j'ai des activités variées":                                                                           "Q5_comp",
    "j'ai l'occasion de développer mes compétences professionnelles":                                                         "Q6_comp",
    # ── Autonomie décisionnelle (auto) ───────────────────────────────────────
    "mon travail me permet souvent de prendre des décisions moi-même":                                                        "Q1_auto",
    "dans ma tâche, j'ai très peu de liberté pour décider comment je fais mon travail":                                       "Q2_auto",
    "j'ai la possibilité d'influencer le déroulement de mon travail":                                                         "Q3_auto",
    # ── Demande psychologique (dem) ──────────────────────────────────────────
    "mon travail me demande de travailler très vite":                                                                         "Q1_dem",
    "mon travail demande de travailler intensement":                                                                          "Q2_dem",
    "on me demande d'effectuer une quantité de travail excessive":                                                            "Q3_dem",
    "je dispose du temps nécessaire pour effectuer correctement mon travail":                                                  "Q4_dem",
    "je reçois des ordres contradictoires de la part d'autres personnes":                                                     "Q5_dem",
    "mon travail nécessite de longues périodes de concentration intense":                                                     "Q6_dem",
    "mes tâches sont souvent interrompues avant d'être achevées, nécessitant de les reprendre plus tard":                     "Q7_dem",
    "mon travail est « très bouscu lé »":                                                                                     "Q8_dem",
    "mon travail est « très bouscu »":                                                                                        "Q8_dem",
    "attendre le travail de collègues ralentit souvent mon propre travail":                                                   "Q9_dem",
    # ── Soutien hiérarchique (sup) ───────────────────────────────────────────
    "mon supérieur se sent concerné par le bien-être de ses subordonnés":                                                     "Q1_sup",
    "mon supérieur prête attention à ce que je dis":                                                                          "Q2_sup",
    "mon supérieur m'aide à mener ma tâche à bien":                                                                           "Q3_sup",
    "mon supérieur réussit facilement à faire collaborer ses subordonnés":                                                    "Q4_sup",
    # ── Soutien des collègues (col) ──────────────────────────────────────────
    "les collègues avec qui je travaille sont des gens professionnellement compétent":                                        "Q1_col",
    "les collègues avec qui je travaille me manifestent de l'intérêt":                                                        "Q2_col",
    "les collègues avec qui je travaille sont amicaux":                                                                       "Q3_col",
    "les collègues avec qui je travaille m'aident à mener les tâches à bien":                                                 "Q4_col",
    # ── Reconnaissance (rec) ────────────────────────────────────────────────
    "on me traite injustement dans mon travail":                                                                              "Q1_rec",
    "ma sécurité d'emploi est menacée":                                                                                       "Q2_rec",
    "ma position professionnelle actuelle correspond bien à ma formation":                                                    "Q3_rec",
    "vu tous mes efforts, je reçois le respect et l'estime que je mérite":                                                    "Q4_rec",
    "vu tous mes efforts, mes perspectives de promotion sont satisfaisantes":                                                  "Q5_rec",
    "vu tous mes efforts, mon salaire est satisfaisant":                                                                      "Q6_rec",
    # ── Équité (equ) ────────────────────────────────────────────────────────
    "la charge de travail est répartie équitablement dans mon équipe":                                                        "Q1_equ",
    # ── Culture (cult) ──────────────────────────────────────────────────────
    "je m'identifie à la culture de l'entreprise?":                                                                           "Q1_cult",
    "je recommanderai ma compagnie à mes connaissances à la recherche d'un emploi":                                           "Q2_cult",
    # ── Satisfaction (sat) ──────────────────────────────────────────────────
    "je suis satisfait de mon travail dans la compagnie":                                                                     "Q1_sat",
    # ── Adéquation ressources / objectifs ───────────────────────────────────
    "je sais ce que je dois faire pour atteindre les objectifs qui me sont fixés":                                            "Q1_adq_resources",
    "je dispose de toutes les ressources nécessaires à l'accomplissement de mes taches quotidiennes":                         "Q2_adq_resources",
    # ── Adéquation formation / rôle ──────────────────────────────────────────
    "mes besoins de formations sont bien pris en compte":                                                                     "Q1_adq_role",
    "les formations dispensées sont cohérentes avec les taches dont j'ai la responsabilité ou qui me sont assignées":        "Q2_adq_role",
}

#  TABLEAUX CROISÉS  — variables sociodémographiques vs. scores de risque et de climat

CROSSTABS_RISK_CORE = [
    ("Genre",                             "Karasek_quadrant_theoretical"),
    ("Tranche_age",                       "Karasek_quadrant_theoretical"),
    ("Tranche_anciennete",                "Karasek_quadrant_theoretical"),
    ("Categorie_IMC",                     "Karasek_quadrant_theoretical"),
    ("IMC_binaire",                       "Karasek_quadrant_theoretical"),
    ("Avez-vous une maladie chronique",   "Karasek_quadrant_theoretical"),
    ("Pratique reguliere du sport",       "Karasek_quadrant_theoretical"),
    ("Catégorie Socio",                   "Karasek_quadrant_theoretical"),
    ("Categorie Socio",                   "Karasek_quadrant_theoretical"),
    ("Situation matrimonial",             "Karasek_quadrant_theoretical"),
]

CROSSTABS_SOCIO_RPS = [
    ("Genre",                             "Iso_strain_theoretical"),
    ("Tranche_age",                       "Iso_strain_theoretical"),
    ("Tranche_anciennete",                "Iso_strain_theoretical"),
    ("Categorie_IMC",                     "Iso_strain_theoretical"),
    ("Avez-vous une maladie chronique",   "Iso_strain_theoretical"),
    ("Situation matrimonial",             "Iso_strain_theoretical"),
    ("Genre",                             "Job_strain_theoretical"),
    ("Tranche_age",                       "Job_strain_theoretical"),
    ("Tranche_anciennete",                "Job_strain_theoretical"),
    ("Categorie_IMC",                     "Job_strain_theoretical"),
    ("Pratique reguliere du sport",       "Job_strain_theoretical"),
    ("Avez-vous une maladie chronique",   "Job_strain_theoretical"),
    ("Situation matrimonial",             "Job_strain_theoretical"),
]

CROSSTABS_CLIMATE = [
    ("sat_score_theo_cat",      "cult_score_theo_cat"),
    ("Genre",                    "cult_score_theo_cat"),
    ("Tranche_age",              "cult_score_theo_cat"),
    ("Tranche_anciennete",       "cult_score_theo_cat"),
    ("Genre",                     "equ_score_theo_cat"),
    ("Tranche_age",               "equ_score_theo_cat"),
    ("Tranche_anciennete",        "equ_score_theo_cat"),
]

CROSSTABS_SOCIO_CLIMATE = [
    ("SS_score_theo_cat",            "sat_score_theo_cat"),
    ("col_score_theo_cat",           "sat_score_theo_cat"),
    ("sup_score_theo_cat",           "sat_score_theo_cat"),
    ("rec_score_theo_cat",           "sat_score_theo_cat"),
    ("equ_score_theo_cat",           "sat_score_theo_cat"),
    ("adq_resources_score_theo_cat", "sat_score_theo_cat"),
    ("adq_role_score_theo_cat",      "sat_score_theo_cat"),
    ("Genre",             "rec_score_theo_cat"),
    ("Tranche_age",       "rec_score_theo_cat"),
    ("Tranche_anciennete","rec_score_theo_cat"),
]

ALL_CROSSTABS = (
    CROSSTABS_RISK_CORE
    + CROSSTABS_SOCIO_RPS
    + CROSSTABS_CLIMATE
    + CROSSTABS_SOCIO_CLIMATE
)

VAR_LABELS = {
    "Genre":                   "le genre",
    "Situation matrimonial":   "la situation matrimoniale",
    "Catégorie Socio":         "la catégorie socioprofessionnelle",
    "Categorie Socio":         "la catégorie socioprofessionnelle",
    "Direction":               "la direction",
    "Fonction":                "la fonction",
    "Poste de travail":        "le poste de travail",
    "Tranche_age":             "la tranche d'âge",
    "Tranche_age_binaire":     "la tranche d'âge (binaire)",
    "Tranche_anciennete":      "l'ancienneté",
    "Categorie_IMC":           "la catégorie IMC (OMS)",
    "IMC_binaire":             "l'IMC (normal / surpoids-obésité)",
    "Consommation reguliere d\u2019alcool": "la consommation régulière d'alcool",
    "Consommation reguliere d'alcool":    "la consommation régulière d'alcool",
    "tabagisme":               "le tabagisme",
    "Pratique reguliere du sport": "la pratique régulière du sport",
    "Avez-vous un handicap physique":  "la présence d'un handicap physique",
    "Avez-vous une maladie chronique": "la présence d'une maladie chronique",
    "Avez-vous \u00e9t\u00e9 suivi pour un probleme psychologique *": "le suivi psychologique",
    "Dem_score_theo_cat":           "le niveau de demande psychologique",
    "Lat_score_theo_cat":           "le niveau de latitude décisionnelle",
    "SS_score_theo_cat":            "le niveau de soutien social",
    "comp_score_theo_cat":          "le niveau d'utilisation des compétences",
    "auto_score_theo_cat":          "le niveau d'autonomie décisionnelle",
    "sup_score_theo_cat":           "le niveau de soutien hiérarchique",
    "col_score_theo_cat":           "le niveau de soutien des collègues",
    "rec_score_theo_cat":           "le niveau de reconnaissance",
    "equ_score_theo_cat":           "le niveau d'équité de charge",
    "cult_score_theo_cat":          "le niveau d'adhésion à la culture",
    "adq_resources_score_theo_cat": "le niveau d'adéquation ressources / objectifs",
    "adq_role_score_theo_cat":      "le niveau d'adéquation formation / rôle",
    "sat_score_theo_cat":           "le niveau de satisfaction au travail",
    "Karasek_quadrant_theoretical": "le quadrant de Karasek",
    "Job_strain_theoretical":       "le Job Strain ",
    "Iso_strain_theoretical":       "l'Isolement au Travail ",
}
