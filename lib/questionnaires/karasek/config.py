from typing import Dict, List

class KarasekConfig:
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
        "Mon travail est \u00ab\u00a0tr\u00e8s bouscu l\u00e9\u00a0\u00bb ":              "Q8_dem",
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
        "Je dispose de toutes les ressources n\u00e9cessaires \u00e0 l\u2019accomplissement de mes taches quotidiennes": "Q2_adq_resources",
        "Mes besoins de formations sont bien pris en compte":                               "Q1_adq_role",
        "Les formations dispens\u00e9es sont coh\u00e9rentes avec les taches dont j\u2019ai la responsabilit\u00e9 ou qui me sont assign\u00e9es": "Q2_adq_role",
    }


    # --- Items à inverser ---
    INVERT_ITEMS: List[str] = ["Q2_auto", "Q2_comp", "Q4_dem", "Q1_rec", "Q2_rec"]

    # --- Calcul des scores ---
    SCORE_MULTIPLIERS: Dict[str, int] = {
        "comp": 2,
        "auto": 4,
        "dem": 1,
        "sup": 1,
        "col": 1,
    }

    KARASEK_SCORE_COMPOSITION: Dict[str, List[str]] = {
        "Dem_score": ["dem_score"],
        "Lat_score": ["comp_score", "auto_score"],
        "SS_score":  ["sup_score",  "col_score"],
    }

    RH_SCORE_GROUPS: List[str] = ["rec", "equ", "cult", "adq_resources", "adq_role", "sat"]

    # --- SEUILS THÉORIQUES (UNIQUEMENT) ---
    # Basés sur le point médian de l'échelle (2.5 * n_items * multiplier
    THRESHOLDS: Dict[str, float] = {
        # Karasek Core
        "Dem_score": 22.5,
        "Lat_score": 60.0,
        "SS_score":  20.0,
        "comp_score": 30.0,
        "auto_score": 30.0,
        "sup_score":  10.0,
        "col_score":  10.0,
        
        # RH Scores
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
        "sat_score":           "Satisfaction au travail",
        "adq_resources_score": "Adéquation ressources / objectifs",
        "adq_role_score":      "Adéquation formation / rôle",
    }
    
    COMPANY_NAME = "COMPANY NAME" 