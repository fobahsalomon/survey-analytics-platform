/**
 * Constantes de l'application
 */

// Types de questionnaires supportés
export const QUESTIONNAIRE_TYPES = {
  KARASEK: 'karasek',
  QVT: 'qvt',
  MBI: 'mbi',
}

export const QUESTIONNAIRE_LABELS = {
  [QUESTIONNAIRE_TYPES.KARASEK]: 'Karasek',
  [QUESTIONNAIRE_TYPES.QVT]: 'QVT',
  [QUESTIONNAIRE_TYPES.MBI]: 'MBI',
}

export const QUESTIONNAIRE_DESCRIPTIONS = {
  [QUESTIONNAIRE_TYPES.KARASEK]: 'Modèle Demande-Contrôle-Soutien pour l\'évaluation du stress au travail',
  [QUESTIONNAIRE_TYPES.QVT]: 'Qualité de Vie au Travail - Évaluation globale du bien-être',
  [QUESTIONNAIRE_TYPES.MBI]: 'Maslach Burnout Inventory - Évaluation de l\'épuisement professionnel',
}

// Dimensions RH pour le radar chart
export const RH_DIMENSIONS = [
  { key: 'rec_score', label: 'Reconnaissance' },
  { key: 'equ_score', label: 'Équité de charge' },
  { key: 'cult_score', label: 'Culture d\'entreprise' },
  { key: 'sat_score', label: 'Satisfaction' },
  { key: 'adq_resources_score', label: 'Ressources & Objectifs' },
  { key: 'sup_score', label: 'Soutien management' },
  { key: 'adq_role_score', label: 'Formation' },
  { key: 'comp_score', label: 'Compétences' },
]

// Variables démographiques disponibles
export const DEMO_VARIABLES = [
  { key: 'Genre', label: 'Genre' },
  { key: 'Tranche_age', label: 'Tranche d\'âge' },
  { key: 'Tranche_anciennete', label: 'Ancienneté' },
  { key: 'Categorie Socio', label: 'Catégorie socioprofessionnelle' },
  { key: 'Categorie_IMC', label: 'Catégorie IMC' },
  { key: 'IMC_binaire', label: 'IMC (normal / surpoids)' },
  { key: 'Direction', label: 'Direction' },
  { key: 'tabagisme', label: 'Tabagisme' },
  { key: 'Consommation reguliere d\'alcool', label: 'Consommation d\'alcool' },
  { key: 'Pratique reguliere du sport', label: 'Pratique sportive' },
  { key: 'Avez-vous une maladie chronique', label: 'Maladie chronique' },
]

// Variables pour les croisements
export const CROSS_TAB_VARIABLES = [
  { key: null, label: 'Aucun croisement' },
  { key: 'Karasek_quadrant_theoretical', label: 'Quadrant Karasek' },
  { key: 'Dem_score_theo_cat', label: 'Charge mentale' },
  { key: 'Lat_score_theo_cat', label: 'Autonomie décisionnelle' },
  { key: 'SS_score_theo_cat', label: 'Soutien social' },
  { key: 'rec_score_theo_cat', label: 'Reconnaissance' },
  { key: 'sat_score_theo_cat', label: 'Satisfaction' },
  { key: 'cult_score_theo_cat', label: 'Culture d\'entreprise' },
  { key: 'equ_score_theo_cat', label: 'Équité de charge' },
]

// Seuils théoriques Karasek
export const KARASEK_THRESHOLDS = {
  Dem_score: 22.5,
  Lat_score: 60.0,
  SS_score: 20.0,
  comp_score: 30.0,
  auto_score: 30.0,
  sup_score: 10.0,
  col_score: 10.0,
}

// Options de filtres
export const FILTER_OPTIONS = {
  all: 'Tous',
  homme: 'Homme',
  femme: 'Femme',
}

// Messages d'erreur
export const ERROR_MESSAGES = {
  FILE_TOO_LARGE: 'Fichier trop volumineux (max 50 Mo)',
  INVALID_FORMAT: 'Format de fichier non supporté. Utilisez un fichier CSV.',
  UPLOAD_FAILED: 'Échec de l\'upload. Veuillez réessayer.',
  ANALYSIS_FAILED: 'Erreur lors de l\'analyse. Vérifiez vos données.',
  NETWORK_ERROR: 'Impossible de contacter le serveur. Vérifiez votre connexion.',
}

// Messages de succès
export const SUCCESS_MESSAGES = {
  UPLOAD_SUCCESS: 'Fichier uploadé avec succès',
  ANALYSIS_COMPLETE: 'Analyse terminée',
  REPORT_DOWNLOADED: 'Rapport téléchargé',
}

export default {
  QUESTIONNAIRE_TYPES,
  QUESTIONNAIRE_LABELS,
  QUESTIONNAIRE_DESCRIPTIONS,
  RH_DIMENSIONS,
  DEMO_VARIABLES,
  CROSS_TAB_VARIABLES,
  KARASEK_THRESHOLDS,
  FILTER_OPTIONS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
}