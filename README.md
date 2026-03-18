# SurveyLens — Plateforme d'analyse des risques psychosociaux

Dashboard multi-questionnaires pour l'analyse du bien-être au travail.

---

## Structure du projet

```
SurveyLens/
├── app.py                          # Page d'accueil (hub de navigation)
├── requirements.txt
├── .streamlit/
│   └── config.toml                 # Thème SurveyLens
│
├── pages/
│   ├── _ui_shared.py               # Composants UI partagés (CSS, jauges, charts)
│   ├── 1_karasek.py                # Dashboard Karasek DCS
│   ├── 2_qvt.py                    # Dashboard QVT
│   └── 3_mbi.py                    # Dashboard MBI Burnout
│
└── lib/
    ├── common/
    │   ├── base_questionnaire.py   # Interface abstraite (ABC)
    │   ├── common_cleaning.py      # Nettoyage PII, socio-démo, Likert
    │   └── file_utils.py           # Chargement CSV / Excel
    │
    ├── data/
    │   ├── sample_karasek.csv      # Données de test Karasek
    │   ├── sample_qvt.csv          # Données de test QVT
    │   └── sample_mbi.csv          # Données de test MBI
    │
    └── questionnaires/
        ├── karasek/
        │   ├── config.py           # Seuils, mappings, couleurs
        │   ├── questionnaire.py    # Pipeline clean → score → classify
        │   ├── analytics.py        # Indicateurs agrégés
        │   └── reporting.py        # Export Word (.docx)
        ├── qvt/
        │   └── (même structure)
        └── mbi/
            └── (même structure)
```

---

## Installation

```fish
# Cloner / copier le dossier SurveyLens
cd SurveyLens

# Installer les dépendances (fish shell)
pip install -r requirements.txt --break-system-packages

# Lancer l'application
streamlit run app.py
```

---

## Questionnaires

### Karasek DCS
Modèle Demande–Contrôle–Soutien (Karasek & Theorell).
- Seuils **théoriques uniquement** (point médian de l'échelle Likert 1–4)
- Quadrants : Actif / Détendu / Tendu / Passif
- Indicateurs : Job Strain, Iso-Strain, scores RH
- Fichier test : `lib/data/sample_karasek.csv`

### QVT
Qualité de Vie au Travail — cadre ANACT / ANI 2013.
- 6 dimensions : Relations, Contenu, Environnement, Organisation, Développement, Équilibre
- Échelle Likert 1–5
- Fichier test : `lib/data/sample_qvt.csv`

### MBI Burnout
Maslach Burnout Inventory — General Survey (MBI-GS), Schaufeli et al. 1996.
- 3 dimensions : Épuisement, Cynisme, Efficacité personnelle
- Échelle de fréquence 0–6
- Score composite de risque burnout
- Fichier test : `lib/data/sample_mbi.csv`

---

## Export Word

Chaque page dashboard contient dans la sidebar un bouton **"Générer rapport Word"**.
Saisir le nom de l'organisation, cliquer, puis télécharger le `.docx` généré.

Requiert : `python-docx>=1.1.0`

---

## Ajouter un nouveau questionnaire

1. Créer `lib/questionnaires/mon_questionnaire/`
2. Implémenter les 4 fichiers : `config.py`, `questionnaire.py`, `analytics.py`, `reporting.py`
3. La classe principale doit hériter de `lib.common.BaseQuestionnaire`
4. Créer `pages/N_mon_questionnaire.py` en utilisant `_ui_shared.py`
5. Ajouter la carte dans `app.py`

---

## Notes

- Tous les seuils sont **théoriques et non cliniques**
- Les données PII (nom, email, téléphone) sont automatiquement supprimées au chargement
- Compatible fish shell (pas de scripts bash `source`)
