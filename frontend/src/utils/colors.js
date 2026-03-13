/**
 * Palette de couleurs pour les visualisations
 */
export const COLORS = {
// Couleurs principales de l'interface
primary: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    500: '#0ea5e9',
    600: '#0284c7',
    700: '#0369a1',
},
secondary: '#f97316',
success: '#22c55e',
warning: '#f59e0b',
danger: '#ef4444',
muted: '#6b88a8',

// Quadrants Karasek
karasek: {
    actif: '#22c55e',      // Vert - High Control, High Demand
    detendu: '#38a3e8',    // Bleu - High Control, Low Demand
    tendu: '#ef4444',      // Rouge - Low Control, High Demand
    passif: '#94a3b8',     // Gris - Low Control, Low Demand
},

// Job Strain / Iso Strain
strain: {
    present: '#ef4444',
    absent: '#22c55e',
},

// Scores binaires (Faible/Élevé)
score: {
    faible: '#ef4444',
    eleve: '#22c55e',
},

// Palette pour graphiques catégoriels
categorical: [
    '#38a3e8', '#f97316', '#22c55e', '#ef4444',
    '#a78bfa', '#06b6d4', '#fb923c', '#84cc16',
    '#f472b6', '#6366f1',
],

// Dégradés
gradients: {
    primary: 'from-primary-500 to-primary-600',
    secondary: 'from-secondary-500 to-secondary-600',
    success: 'from-green-400 to-green-600',
    warning: 'from-amber-400 to-amber-600',
    danger: 'from-red-400 to-red-600',
},
}

/**
 * Obtient la couleur pour une catégorie Karasek
 */
export const getKarasekColor = (quadrant) => {
const map = {
    'Actif': COLORS.karasek.actif,
    'Active': COLORS.karasek.actif,
    'Détendu': COLORS.karasek.detendu,
    'Detendu': COLORS.karasek.detendu,
    'Relaxed': COLORS.karasek.detendu,
    'Tendu': COLORS.karasek.tendu,
    'Tense': COLORS.karasek.tendu,
    'Passif': COLORS.karasek.passif,
    'Passive': COLORS.karasek.passif,
}
return map[quadrant] || COLORS.muted
}

/**
 * Obtient la couleur pour un score binaire
 */
export const getBinaryScoreColor = (value, isInverted = false) => {
const isHigh = ['Élevé', 'Eleve', 'High', 'Présent'].includes(value)
const isFavorable = isInverted ? !isHigh : isHigh

return isFavorable ? COLORS.success : COLORS.danger
}

export default COLORS