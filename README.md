# SurveyLens

SurveyLens est une application Streamlit d'analyse de questionnaires RH et RPS.

Le projet permet de :
- charger un fichier CSV ou Excel ;
- nettoyer les données ;
- calculer des scores questionnaire par questionnaire ;
- produire des indicateurs agrégés ;
- afficher un dashboard interactif ;
- générer un rapport Word et un export ZIP avec les figures.

Le dépôt contient actuellement 3 modules d'analyse :
- `Karasek` : stress au travail, Job Strain, Iso-Strain, quadrants ;
- `QVT` : qualité de vie au travail ;
- `MBI` : burnout selon le Maslach Burnout Inventory.

## À quoi sert le projet

L'application sert de couche de présentation au-dessus d'un moteur d'analyse.

Le principe est toujours le même :
1. l'utilisateur charge un fichier ;
2. le fichier est converti en `DataFrame` pandas ;
3. le pipeline du questionnaire nettoie, score et classe les réponses ;
4. les analytics produisent les KPI et distributions ;
5. les visualisations et le reporting utilisent ces résultats ;
6. le dashboard affiche le tout dans Streamlit.

## Structure du projet

```text
survey-analytics-platform/
├── app.py
├── README.md
├── architecture.md
├── requirements.txt
├── pages/
│   ├── 1_karasek.py
│   ├── 2_qvt.py
│   ├── 3_mbi.py
│   ├── _ui_shared.py
│   └── _export_utils.py
└── lib/
    ├── common/
    │   ├── __init__.py
    │   ├── base_questionnaire.py
    │   ├── common_cleaning.py
    │   └── file_utils.py
    ├── data/
    │   ├── sample_karasek1.csv
    │   ├── sample_karasek2.csv
    │   ├── sample_qvt.csv
    │   └── sample_mbi.csv
    └── questionnaires/
        ├── karasek/
        ├── qvt/
        └── mbi/
```

## Rôle des dossiers

### `app.py`

Page d'accueil.

Elle ne calcule pas de scores. Elle sert uniquement de hub de navigation vers les trois dashboards.

### `pages/`

Contient les pages Streamlit.

Chaque page questionnaire :
- gère l'upload ;
- exécute le pipeline ;
- applique les filtres ;
- affiche les KPI, graphiques et tableaux ;
- pilote l'export Word et ZIP.

Les deux fichiers spéciaux sont :
- `pages/_ui_shared.py` : composants UI réutilisables ;
- `pages/_export_utils.py` : logique ZIP et boutons de téléchargement.

### `lib/common/`

Contient le socle partagé :
- lecture de fichiers ;
- nettoyage commun ;
- enrichissement socio-démographique ;
- interface abstraite des questionnaires.

### `lib/questionnaires/`

Chaque sous-dossier suit la même idée :
- `config.py` : constantes, seuils, mappings, labels, couleurs ;
- `questionnaire.py` : pipeline principal ;
- `analytics.py` : calculs agrégés pour le dashboard ;
- `visualizations.py` : figures PNG ;
- `reporting.py` : génération du document Word.

## Pipeline technique

Le flux principal est :

```text
Fichier brut
  -> load_dataframe(...)
  -> Questionnaire.clean(...)
  -> Questionnaire.score(...)
  -> Questionnaire.classify(...)
  -> Questionnaire.analytics(...)
  -> Visualizations.generate_all(...)
  -> Reporting.generate(...)
```

## Installation

### Prérequis

- Python 3.11 ou plus récent recommandé
- `pip`

### Installation

```bash
pip install -r requirements.txt
```

### Lancement

```bash
streamlit run app.py
```

## Dépendances importantes

- `streamlit` : interface web
- `pandas` : manipulation des données
- `numpy` : calcul numérique
- `plotly` : graphiques interactifs
- `matplotlib` et `seaborn` : figures exportées en PNG
- `python-docx` : génération des rapports Word

## Fichiers d'exemple

Des jeux de données d'exemple sont présents dans [lib/data](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/lib/data).

Ils servent à :
- tester rapidement l'application ;
- comprendre le format attendu ;
- valider les visualisations et les rapports.

## Gestion des données

Le projet supprime automatiquement certaines colonnes sensibles ou inutiles :
- nom ;
- prénom ;
- email ;
- téléphone ;
- colonnes vides ou quasi vides.

Le projet enrichit aussi les données quand c'est possible :
- tranche d'âge ;
- tranche d'ancienneté ;
- IMC ;
- catégories dérivées utiles aux tableaux croisés.

Quand un fichier ne contient pas `Age` mais contient une tranche d'âge, le projet sait maintenant estimer l'âge moyen et filtrer sur l'âge à partir de cette tranche.

## Questionnaires pris en charge

### Karasek

But :
- mesurer la demande psychologique ;
- la latitude décisionnelle ;
- le soutien social ;
- les zones de tension au travail.

Sorties clés :
- quadrants Karasek ;
- Job Strain ;
- Iso-Strain ;
- scores RH complémentaires.

### QVT

But :
- mesurer le bien-être organisationnel sur plusieurs dimensions.

Sorties clés :
- score global QVT ;
- distribution par dimension ;
- répartition satisfaisant / mitigé / insatisfaisant.

### MBI

But :
- mesurer le risque de burnout.

Sorties clés :
- épuisement ;
- cynisme ;
- efficacité personnelle ;
- risque de burnout composite.

## Reporting et exports

Chaque page peut produire :
- un rapport Word `.docx` ;
- un ZIP contenant le rapport et toutes les figures PNG.

Le reporting s'appuie sur les métriques agrégées déjà calculées. Il ne recalcule pas la logique métier depuis zéro.

## Ajouter un nouveau questionnaire

La manière la plus simple est de copier la structure d'un module existant.

Étapes :
1. créer `lib/questionnaires/mon_module/` ;
2. ajouter `config.py` ;
3. ajouter `questionnaire.py` ;
4. ajouter `analytics.py` ;
5. ajouter `visualizations.py` si nécessaire ;
6. ajouter `reporting.py` ;
7. créer une page Streamlit dans `pages/`.

La classe questionnaire doit hériter de `BaseQuestionnaire`.

## Philosophie du code

Le projet sépare volontairement :
- la logique métier ;
- la présentation ;
- l'export ;
- les constantes.

Cette séparation permet :
- de modifier les seuils sans toucher au dashboard ;
- de changer l'UI sans casser les calculs ;
- de réutiliser les mêmes métriques pour les graphiques et les rapports.

## Documentation complémentaire

Le fichier [architecture.md](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/architecture.md) décrit en détail :
- les couches du projet ;
- le rôle de chaque fichier important ;
- le cycle de vie complet d'une donnée ;
- la logique de chaque questionnaire ;
- les conventions de développement.
