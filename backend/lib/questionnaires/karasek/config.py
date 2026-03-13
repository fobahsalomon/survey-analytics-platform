from typing import Dict, List, Tuple
import textwrap
import unicodedata

class KarasekConfig:
    COMPANY_NAME = "COMPANY NAME"
    FIGURES_DIR = "reports/karasek/figures"
    
    # ── Renommage Likert ────────────────────────────────────────────────────
    # --- Mapping des colonnes (Question -> Code) ---
    RENAME_MAPPING: Dict[str, str] = {
        "Dans mon travail, je dois apprendre des choses nouvelles":                        "Q1_comp",
        "Dans mon travail j\u2019effectue des t\u00e2ches r\u00e9p\u00e9titives":         "Q2_comp",
        "Mon travail me demande d\u2019\u00eatre cr\u00e9atif":                            "Q3_comp",
        "Mon travail me demande un haut niveau de comp\u00e9tence":                        "Q4_comp",
        "Dans mon travail, j\u2019ai des activit\u00e9s vari\u00e9es":                    "Q5_comp",
        "J\u2019ai l\u2019occasion de d\u00e9velopper mes comp\u00e9tences professionnelles": "Q6_comp",
        "Mon travail me permet souvent de prendre des d\u00e9cisions moi-m\u00eame":       "Q1_auto",
        "Dans ma t\u00e2che, j\u2019ai tr\u00e8s peu de libert\u00e9 pour d\u00e9cider comment je fais mon travail": "Q2_auto",
        "J\u2019ai la possibilit\u00e9 d\u2019influencer le d\u00e9roulement de mon travail": "Q3_auto",
        "Mon travail me demande de travailler tr\u00e8s vite":                             "Q1_dem",
        "Mon travail demande de travailler intensement":                                    "Q2_dem",
        "On me demande d\u2019effectuer une quantit\u00e9 de travail excessive":            "Q3_dem",
        "Je dispose du temps n\u00e9cessaire pour effectuer correctement mon travail":      "Q4_dem",
        "Je re\u00e7ois des ordres contradictoires de la part d\u2019autres personnes":    "Q5_dem",
        "Mon travail n\u00e9cessite de longues p\u00e9riodes de concentration intense":    "Q6_dem",
        "Mes t\u00e2ches sont souvent interrompues avant d\u2019\u00eatre achev\u00e9es, n\u00e9cessitant de les reprendre plus tard": "Q7_dem",
        "Mon travail est \u00ab\u00a0tr\u00e8s bouscul\u00e9\u00a0\u00bb ":              "Q8_dem",
        "Attendre le travail de coll\u00e8gues ralentit souvent mon propre travail":        "Q9_dem",
        "Mon sup\u00e9rieur se sent concern\u00e9 par le bien-\u00eatre de ses subordonn\u00e9s": "Q1_sup",
        "Mon sup\u00e9rieur pr\u00eate attention \u00e0 ce que je dis":                    "Q2_sup",
        "Mon sup\u00e9rieur m\u2019aide \u00e0 mener ma t\u00e2che \u00e0 bien":           "Q3_sup",
        "Mon sup\u00e9rieur r\u00e9ussit facilement \u00e0 faire collaborer ses subordonn\u00e9s": "Q4_sup",
        "Les coll\u00e8gues avec qui je travaille sont des gens professionnellement comp\u00e9tent": "Q1_col",
        "Les coll\u00e8gues avec qui je travaille me manifestent de l\u2019int\u00e9r\u00eat": "Q2_col",
        "Les coll\u00e8gues avec qui je travaille sont amicaux":                            "Q3_col",
        "Les coll\u00e8gues avec qui je travaille m\u2019aident \u00e0 mener les t\u00e2ches \u00e0 bien": "Q4_col",
        "On me traite injustement dans mon travail":                                        "Q1_rec",
        "Ma s\u00e9curit\u00e9 d\u2019emploi est menac\u00e9e":                             "Q2_rec",
        "Ma position professionnelle actuelle correspond bien \u00e0 ma formation":         "Q3_rec",
        "Vu tous mes efforts, je re\u00e7ois le respect et l\u2019estime que je m\u00e9rite": "Q4_rec",
        "Vu tous mes efforts, mes perspectives de promotion sont satisfaisantes":            "Q5_rec",
        "Vu tous mes efforts, mon salaire est satisfaisant":                                "Q6_rec",
        "La charge de travail est r\u00e9partie \u00e9quitablement dans mon \u00e9quipe":  "Q1_equ",
        "Je m\u2019identifie \u00e0 la culture de l\u2019entreprise?":                     "Q1_cult",
        "Je m'identifie à la culture de l'entreprise?":                                     "Q1_cult",
        "Je recommanderai ma compagnie \u00e0 mes connaissances \u00e0 la recherche d\u2019un emploi": "Q2_cult",
        "Je recommanderai ma compagnie à mes connaissances à la recherche d'un emploi":     "Q2_cult",
        "Je suis satisfait de mon travail dans la compagnie":                               "Q1_sat",
        "Je sais ce que je dois faire pour atteindre les objectifs qui me sont fix\u00e9s": "Q1_adq_resources",
        "Je dispose de toutes les ressources nécessaires à l'accomplissement de mes taches quotidiennes": "Q2_adq_resources",
        "Mes besoins de formations sont bien pris en compte":                               "Q1_adq_role",
        "Les formations dispensées sont cohérentes avec les taches dont j'ai la responsabilité ou qui me sont assignées": "Q2_adq_role",
    }

    # --- Items à inverser ---
    INVERT_ITEMS: List[str] = ["Q2_auto", "Q2_comp", "Q4_dem", "Q1_rec", "Q2_rec"]

    # --- Calcul des scores ---
    SCORE_MULTIPLIERS: Dict[str, int] = {
        "comp": 2,
        "auto": 4,
        "dem":  1,
        "sup":  1,
        "col":  1,
    }

    KARASEK_SCORE_COMPOSITION: Dict[str, List[str]] = {
        "Dem_score": ["dem_score"],
        "Lat_score": ["comp_score", "auto_score"],
        "SS_score":  ["sup_score",  "col_score"],
    }

    RH_SCORE_GROUPS: List[str] = ["rec", "equ", "cult", "adq_resources", "adq_role", "sat"]

    # ── SEUILS THÉORIQUES ────────────────────────────────────────────────────
    THRESHOLDS: Dict[str, float] = {
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

    SCORE_LABELS: Dict[str, str] = {
        "Dem_score":           "Demande psychologique",
        "Lat_score":           "Latitude décisionnelle",
        "SS_score":            "Soutien social",
        "comp_score":          "Utilisation des compétences",
        "auto_score":          "Autonomie décisionnelle",
        "sup_score":           "Soutien hiérarchique",
        "col_score":           "Soutien des collègues",
        "rec_score":           "Reconnaissance",
        "equ_score":           "Équité de charge",
        "cult_score":          "Culture organisationnelle",
        "adq_resources_score": "Adéquation ressources / objectifs",
        "adq_role_score":      "Adéquation formation / rôle",
        "sat_score":           "Satisfaction au travail",
    }

    # ── PALETTES ────────────────────────────────────────────────────────────
    KARASEK_PALETTE = {
        "Actif":   "#22C55E",
        "Detendu": "#38A3E8",
        "Détendu": "#38A3E8",
        "Tendu":   "#EF4444",
        "Passif":  "#94A3B8",
    }

    STRAIN_PALETTE = {"Présent": "#EF4444", "Absent": "#22C55E"}

    # ── LABELS POUR GRAPHIQUES ─────────────────────────────────────────────
    VAR_LABELS: Dict[str, str] = {
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
        "Dem_score_cat":           "le niveau de demande psychologique",
        "Lat_score_cat":           "le niveau de latitude décisionnelle",
        "SS_score_cat":            "le niveau de soutien social",
        "comp_score_cat":          "le niveau d'utilisation des compétences",
        "auto_score_cat":          "le niveau d'autonomie décisionnelle",
        "sup_score_cat":           "le niveau de soutien hiérarchique",
        "col_score_cat":           "le niveau de soutien des collègues",
        "rec_score_cat":           "le niveau de reconnaissance",
        "equ_score_cat":           "le niveau d'équité de charge",
        "cult_score_cat":          "le niveau d'adhésion à la culture",
        "adq_resources_score_cat": "le niveau d'adéquation ressources / objectifs",
        "adq_role_score_cat":      "le niveau d'adéquation formation / rôle",
        "sat_score_cat":           "le niveau de satisfaction au travail",
        "Karasek_quadrant": "le quadrant de Karasek (seuil théorique)",
        "Job_strain":       "le Job Strain (seuil théorique)",
        "Iso_strain":       "l'Isolement au Travail (seuil théorique)",
    }

    # ── VARIABLES CATÉGORIQUES À VISUALISER ────────────────────────────────
    CAT_VARS = [
        "Genre",
        "Situation matrimonial",
        "Tranche_age",
        "Tranche_anciennete",
        "Categorie_IMC",
        "IMC_binaire",
        "Catégorie Socio",
        "Categorie Socio",
        "Consommation reguliere d\u2019alcool",
        "Consommation reguliere d'alcool",
        "tabagisme",
        "Pratique reguliere du sport",
        "Avez-vous un handicap physique",
        "Avez-vous une maladie chronique",
        "Avez-vous \u00e9t\u00e9 suivi pour un probleme psychologique *",
    ]

    # ── TABLEAUX CROISÉS (uniquement théorique) ────────────────────────────
    CROSSTABS_RISK_CORE = [
        ("Genre",                             "Karasek_quadrant"),
        ("Tranche_age",                       "Karasek_quadrant"),
        ("Tranche_anciennete",                "Karasek_quadrant"),
        ("Categorie_IMC",                     "Karasek_quadrant"),
        ("IMC_binaire",                       "Karasek_quadrant"),
        ("Avez-vous une maladie chronique",   "Karasek_quadrant"),
        ("Pratique reguliere du sport",       "Karasek_quadrant"),
        ("Direction",                         "Karasek_quadrant"),
        ("Catégorie Socio",                   "Karasek_quadrant"),
        ("Categorie Socio",                   "Karasek_quadrant"),
        ("Situation matrimonial",             "Karasek_quadrant"),
    ]

    CROSSTABS_SOCIO_RPS = [
        ("Genre",                             "Iso_strain"),
        ("Tranche_age",                       "Iso_strain"),
        ("Tranche_anciennete",                "Iso_strain"),
        ("Categorie_IMC",                     "Iso_strain"),
        ("Avez-vous une maladie chronique",   "Iso_strain"),
        ("Situation matrimonial",             "Iso_strain"),
        ("Genre",                             "Job_strain"),
        ("Tranche_age",                       "Job_strain"),
        ("Tranche_anciennete",                "Job_strain"),
        ("Categorie_IMC",                     "Job_strain"),
        ("Pratique reguliere du sport",       "Job_strain"),
        ("Avez-vous une maladie chronique",   "Job_strain"),
        ("Situation matrimonial",             "Job_strain"),
    ]

    CROSSTABS_CLIMATE = [
        ("sat_score_cat",      "cult_score_cat"),
        ("Genre",                    "cult_score_cat"),
        ("Tranche_age",              "cult_score_cat"),
        ("Tranche_anciennete",       "cult_score_cat"),
        ("Genre",                     "equ_score_cat"),
        ("Tranche_age",               "equ_score_cat"),
        ("Tranche_anciennete",        "equ_score_cat"),
    ]

    CROSSTABS_SOCIO_CLIMATE = [
        ("SS_score_cat",            "sat_score_cat"),
        ("col_score_cat",           "sat_score_cat"),
        ("sup_score_cat",           "sat_score_cat"),
        ("rec_score_cat",           "sat_score_cat"),
        ("equ_score_cat",           "sat_score_cat"),
        ("adq_resources_score_cat", "sat_score_cat"),
        ("adq_role_score_cat",      "sat_score_cat"),
        ("Genre",             "rec_score_cat"),
        ("Tranche_age",       "rec_score_cat"),
        ("Tranche_anciennete","rec_score_cat"),
    ]

    ALL_CROSSTABS = (
        CROSSTABS_RISK_CORE
        + CROSSTABS_SOCIO_RPS
        + CROSSTABS_CLIMATE
        + CROSSTABS_SOCIO_CLIMATE
    )

    # ── ORDRE DES MODALITÉS ────────────────────────────────────────────────
    MODALITY_ORDER: Dict[str, List[str]] = {
        "Genre":               ["Homme", "Femme"],
        "Situation matrimonial": ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf/Veuve"],
        "Tranche_age":         ["20-30 ans", "31-40 ans", "41-50 ans", "51 ans et plus"],
        "Tranche_age_binaire": ["moins de 40 ans", "plus de 40 ans"],
        "Tranche_anciennete":  ["0-2 ans", "3-5 ans", "6-10 ans", "11-20 ans", "21 ans et +"],
        "Categorie_IMC":       ["Insuffisance pondérale", "Corpulence normale", "Surpoids", "Obésité"],
        "IMC_binaire":         ["Normal", "Surpoids/Obésité"],
        "Catégorie Socio":     ["Employé", "Agent de maîtrise", "Cadre"],
        "Categorie Socio":     ["Employé", "Agent de maîtrise", "Cadre"],
        "Consommation reguliere d\u2019alcool": ["Non", "Oui"],
        "Consommation reguliere d'alcool":    ["Non", "Oui"],
        "tabagisme":           ["Non", "Oui"],
        "Pratique reguliere du sport": ["Non", "Oui"],
        "Avez-vous un handicap physique":  ["Non", "Oui"],
        "Avez-vous une maladie chronique": ["Non", "Oui"],
        "Karasek_quadrant": ["Actif", "Detendu", "Passif", "Tendu"],
        "Job_strain":       ["Absent", "Présent"],
        "Iso_strain":       ["Absent", "Présent"],
    }

    SCORE_CAT_ORDER = ["Faible", "Élevé"]