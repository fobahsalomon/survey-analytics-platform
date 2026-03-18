# Architecture du projet SurveyLens

## Vue d'ensemble

SurveyLens est une application d'analyse de questionnaires construite autour d'une architecture simple :
- une couche interface utilisateur en Streamlit ;
- une couche métier par questionnaire ;
- une couche commune pour le chargement et le nettoyage ;
- une couche de restitution pour les graphiques et les rapports.

L'objectif de cette architecture est de garder les responsabilités séparées.

En clair :
- `pages/` affiche ;
- `lib/common/` prépare ;
- `lib/questionnaires/*` calcule ;
- `reporting.py` raconte les résultats ;
- `visualizations.py` les transforme en images.

## Vision mentale simple

Si un enfant devait comprendre le projet, on peut le résumer comme ça :

- le fichier Excel ou CSV est une boîte remplie de réponses ;
- le code ouvre la boîte ;
- il enlève les morceaux inutiles ou mal rangés ;
- il range les réponses dans les bonnes cases ;
- il calcule des scores ;
- il transforme ces scores en cartes, jauges, tableaux et rapports.

## Couches du projet

### 1. Couche application

Fichiers principaux :
- [app.py](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/app.py)
- [pages/1_karasek.py](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/pages/1_karasek.py)
- [pages/2_qvt.py](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/pages/2_qvt.py)
- [pages/3_mbi.py](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/pages/3_mbi.py)

Responsabilité :
- interaction utilisateur ;
- upload de fichiers ;
- application des filtres ;
- affichage des indicateurs ;
- déclenchement des exports.

Cette couche ne doit pas contenir la vraie logique scientifique du questionnaire.
Elle orchestre et présente.

### 2. Couche commune

Fichiers principaux :
- [lib/common/file_utils.py](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/lib/common/file_utils.py)
- [lib/common/common_cleaning.py](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/lib/common/common_cleaning.py)
- [lib/common/base_questionnaire.py](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/lib/common/base_questionnaire.py)

Responsabilité :
- lire les fichiers ;
- détecter CSV ou Excel ;
- nettoyer les colonnes ;
- enrichir les variables socio-démo ;
- imposer une structure commune à tous les questionnaires.

### 3. Couche métier

Pour chaque questionnaire :
- `config.py` stocke les constantes ;
- `questionnaire.py` transforme les réponses individuelles ;
- `analytics.py` résume les résultats à l'échelle de la population ;
- `visualizations.py` produit des PNG ;
- `reporting.py` construit un document Word.

Cette couche est le coeur métier du projet.

### 4. Couche export

Fichiers principaux :
- [pages/_export_utils.py](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/pages/_export_utils.py)
- `reporting.py` dans chaque questionnaire

Responsabilité :
- préparer les fichiers téléchargeables ;
- empaqueter les images ;
- produire un document final lisible.

## Cycle de vie d'une donnée

Voici le parcours complet d'une réponse utilisateur.

### Étape 1 : chargement

La donnée est chargée avec `load_dataframe(...)`.

Cette fonction :
- accepte un chemin, des bytes ou un objet uploadé ;
- détecte automatiquement s'il s'agit d'un CSV ou d'un Excel ;
- nettoie les noms de colonnes en surface.

### Étape 2 : nettoyage

Chaque questionnaire appelle `clean(...)`.

Le nettoyage commun :
- supprime les colonnes sensibles ;
- supprime certaines colonnes trop vides ;
- enrichit les colonnes socio-démo ;
- harmonise des champs utiles comme `Tranche_age`.

### Étape 3 : scoring

Chaque `questionnaire.py` :
- retrouve les colonnes utiles ;
- convertit les items Likert ;
- inverse les questions inversées si besoin ;
- calcule des scores numériques.

### Étape 4 : classification

Les scores sont transformés en catégories métier.

Exemples :
- `Bas / Modéré / Élevé`
- `Satisfaisant / Mitigé / Insatisfaisant`
- `Actif / Tendu / Passif / Détendu`

### Étape 5 : analytics

Les `analytics.py` calculent des métriques prêtes à afficher :
- âge moyen ;
- répartition hommes / femmes ;
- prévalence d'un niveau élevé ;
- moyenne de score ;
- distribution par catégorie.

### Étape 6 : visualisations

Les `visualizations.py` prennent :
- le `DataFrame` enrichi ;
- les métriques déjà calculées.

Ils produisent :
- des figures PNG ;
- stockées en mémoire sous forme de `bytes`.

### Étape 7 : reporting

Le reporting assemble :
- texte ;
- tableaux ;
- chiffres clés ;
- figures.

Le résultat est un document `.docx`.

## Convention des modules questionnaire

Chaque module suit la même structure pour limiter la complexité.

### `config.py`

Contient :
- seuils ;
- labels ;
- mappings de renommage ;
- couleurs ;
- listes de tableaux croisés.

Pourquoi c'est utile :
- on modifie la configuration sans toucher aux calculs ;
- les labels du dashboard restent cohérents ;
- les visualisations réutilisent les mêmes noms.

### `questionnaire.py`

Contient le pipeline sur les lignes du fichier.

C'est ici qu'on transforme les réponses individuelles.

Sortie typique :
- une ligne répondant en entrée ;
- une ligne enrichie avec scores et catégories en sortie.

### `analytics.py`

Contient les calculs agrégés.

Exemple :
- au lieu d'avoir 1 000 lignes individuelles,
- on calcule “42,3% des répondants sont dans tel groupe”.

### `visualizations.py`

Contient la logique de rendu des images.

Le choix de renvoyer des `bytes` PNG est important :
- les pages Streamlit peuvent les afficher ;
- les exports Word peuvent les insérer ;
- le ZIP peut les réutiliser sans recalcul.

### `reporting.py`

Transforme les résultats en document structuré.

Le reporting n'est pas le bon endroit pour recalculer la logique métier.
Il doit consommer des résultats déjà préparés.

## Architecture des pages Streamlit

Chaque page suit presque toujours le même schéma :

1. configuration Streamlit ;
2. import des composants UI ;
3. upload du fichier ;
4. exécution du pipeline questionnaire ;
5. affichage de la sidebar de filtres ;
6. calcul des analytics ;
7. affichage des onglets ;
8. génération optionnelle du rapport et des figures.

Cette répétition est volontaire.
Elle rend les trois pages faciles à comparer et à maintenir.

## Rôle de `_ui_shared.py`

Ce fichier centralise :
- le CSS global ;
- les composants HTML réutilisables ;
- les graphiques Plotly partagés ;
- les filtres de sidebar ;
- quelques helpers de rendu.

Pourquoi c'est important :
- sans ce fichier, les trois pages dupliqueraient énormément de code ;
- l'apparence visuelle resterait moins cohérente ;
- un changement de style demanderait trois modifications.

## Gestion de l'âge et des tranches d'âge

Le projet accepte deux cas :
- un âge numérique réel ;
- une tranche d'âge.

La logique partagée de [common_cleaning.py](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/lib/common/common_cleaning.py) sait :
- trouver une colonne `Age` ;
- sinon trouver une colonne de type `Tranche d’âge` ;
- harmoniser cette tranche en `Tranche_age` ;
- estimer un âge moyen à partir d'un midpoint.

Conséquence :
- les KPI d'âge moyen ;
- les filtres de sidebar ;
- plusieurs visuels démographiques

peuvent fonctionner même si le fichier source n'a pas d'âge exact.

## Données et confidentialité

Le projet enlève automatiquement certaines données personnelles évidentes.

Ce nettoyage n'est pas une anonymisation parfaite, mais une protection de premier niveau.

Il faut retenir :
- le code aide à limiter les colonnes sensibles ;
- il ne remplace pas une vraie politique de gouvernance des données.

## Décisions techniques importantes

### 1. Séparer dashboard et logique métier

Bonne décision car :
- les tests sont plus simples ;
- les bugs sont plus faciles à localiser ;
- les rapports peuvent réutiliser les mêmes résultats.

### 2. Utiliser des configurations par questionnaire

Bonne décision car :
- les seuils et libellés changent souvent ;
- les mappings de colonnes sont plus faciles à relire ;
- les fichiers métier restent plus courts.

### 3. Générer des figures en `bytes`

Bonne décision car :
- on évite les fichiers temporaires ;
- on simplifie l'intégration Word ;
- on réduit le couplage au système de fichiers.

### 4. Gérer le pipeline via `BaseQuestionnaire`

Bonne décision car :
- tous les modules parlent le même langage ;
- ajouter un nouveau questionnaire devient plus simple ;
- les pages Streamlit n'ont pas besoin de connaître tous les détails internes.

## Ce qu'il faut modifier selon le besoin

### Changer des seuils

Modifier :
- `config.py` du questionnaire concerné.

### Changer le calcul d'un score

Modifier :
- `questionnaire.py`

### Changer un KPI ou un agrégat

Modifier :
- `analytics.py`

### Changer une image exportée

Modifier :
- `visualizations.py`

### Changer le contenu du rapport Word

Modifier :
- `reporting.py`

### Changer le look de l'application

Modifier en priorité :
- [pages/_ui_shared.py](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/pages/_ui_shared.py)
- [app.py](/home/fobah-salomon/OneDrive/workspace/GitHub/survey-analytics-platform/app.py)

## Ajouter un questionnaire proprement

Checklist recommandée :

1. créer le dossier du nouveau questionnaire ;
2. définir les mappings et seuils dans `config.py` ;
3. implémenter le pipeline dans `questionnaire.py` ;
4. produire les métriques dans `analytics.py` ;
5. ajouter le reporting ;
6. ajouter les visualisations si le module en a besoin ;
7. créer une page Streamlit ;
8. ajouter le lien dans `app.py`.

## Risques de maintenance à surveiller

Les zones les plus sensibles sont :
- les mappings de colonnes de fichiers réels ;
- les différences d'orthographe ou d'accents ;
- la cohérence entre `analytics`, `visualizations` et `reporting` ;
- les colonnes dérivées comme `Tranche_age`, `IMC_binaire`, catégories de score.

Si un dashboard affiche des résultats incohérents, vérifier d'abord :
1. les noms de colonnes après nettoyage ;
2. les catégories créées par `classify(...)` ;
3. les colonnes attendues par les visualisations ;
4. les seuils dans `config.py`.

## Résumé simple

SurveyLens est un projet où :
- `pages/` montre ;
- `lib/common/` prépare ;
- `lib/questionnaires/` réfléchit ;
- `reporting.py` écrit ;
- `visualizations.py` dessine.

Si on garde cette règle en tête, le projet reste compréhensible même quand il grandit.
