/**
 * Formate un nombre avec séparateur de milliers
 */
export const formatNumber = (num, decimals = 0) => {
if (num === null || num === undefined || isNaN(num)) return '-'
return new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
}).format(num)
}

/**
 * Formate un pourcentage
 */
export const formatPercent = (value, decimals = 1) => {
if (value === null || value === undefined || isNaN(value)) return '-'
return `${formatNumber(value, decimals)}%`
}

/**
 * Formate un effectif avec pourcentage
 */
export const formatCount = (count, total, decimals = 1) => {
if (!total || total === 0) return formatNumber(count)
const pct = (count / total) * 100
return `${formatNumber(count)} (${formatPercent(pct, decimals)})`
}

/**
 * Formate une date
 */
export const formatDate = (dateString) => {
if (!dateString) return '-'
return new Date(dateString).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
})
}

/**
 * Capitalize une chaîne avec gestion des articles
 */
export const smartCapitalize = (text) => {
if (!text) return ''
const lowerWords = ['le', 'la', 'les', 'de', 'du', 'des', 'au', 'aux', "d'", "l'"]

return text
    .split(' ')
    .map((word, index) => {
    const lower = word.toLowerCase()
    if (index === 0) return word.charAt(0).toUpperCase() + word.slice(1)
    if (lowerWords.includes(lower) || lower.startsWith("l'") || lower.startsWith("d'")) {
        return lower
    }
    return word.charAt(0).toUpperCase() + word.slice(1)
    })
    .join(' ')
}

/**
 * Tronque un texte avec points de suspension
 */
export const truncate = (text, maxLength = 50) => {
if (!text || text.length <= maxLength) return text
return text.slice(0, maxLength) + '...'
}

/**
 * Obtient la classe de couleur pour un pourcentage
 */
export const getColorClass = (pct, thresholds = [35, 60]) => {
if (pct < thresholds[0]) return 'text-success'
if (pct > thresholds[1]) return 'text-danger'
return 'text-warning'
}

/**
 * Obtient la couleur de fond pour un pourcentage
 */
export const getBgClass = (pct, thresholds = [35, 60]) => {
if (pct < thresholds[0]) return 'bg-success/10'
if (pct > thresholds[1]) return 'bg-danger/10'
return 'bg-warning/10'
}

/**
 * Normalise une chaîne pour la comparaison (accents, espaces)
 */
export const normalizeText = (text) => {
if (!text) return ''
return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ')
}

export default {
formatNumber,
formatPercent,
formatCount,
formatDate,
smartCapitalize,
truncate,
getColorClass,
getBgClass,
normalizeText,
}