// frontend/src/components/layout/FilterBar.jsx
import { RefreshCw } from 'lucide-react'
import { useAnalysis } from '../../hooks/useAnalysis'
import { formatNumber } from '../../utils/formatters'

export default function FilterBar() {
const { state, updateFilters } = useAnalysis()
const { filters, metrics } = state

// Options statiques pour les filtres (à adapter selon tes données réelles)
const filterOptions = {
    direction: ['Tous', 'Direction A', 'Direction B', 'Direction C'],
    csp: ['Tous', 'Employé', 'Agent de maîtrise', 'Cadre'],
    genre: ['Tous', 'Homme', 'Femme'],
    ageRange: { min: 20, max: 65 },
}

const handleReset = () => {
    updateFilters({
    direction: 'Tous',
    csp: 'Tous',
    genre: 'Tous',
    ageRange: [20, 65],
    })
}

return (
    <div className="card mb-6 sticky top-20 z-40 bg-white/95 backdrop-blur-sm">
    <div className="flex flex-wrap items-end gap-4">
        {/* Direction */}
        <div className="flex-1 min-w-[180px]">
        <label className="block text-xs font-semibold text-primary-700 uppercase tracking-wide mb-1.5">
            Direction
        </label>
        <select
            value={filters.direction}
            onChange={(e) => updateFilters({ direction: e.target.value })}
            className="select"
        >
            {filterOptions.direction.map((opt) => (
            <option key={opt} value={opt}>
                {opt}
            </option>
            ))}
        </select>
        </div>

        {/* CSP */}
        <div className="flex-1 min-w-[180px]">
        <label className="block text-xs font-semibold text-primary-700 uppercase tracking-wide mb-1.5">
            Catégorie socio
        </label>
        <select
            value={filters.csp}
            onChange={(e) => updateFilters({ csp: e.target.value })}
            className="select"
        >
            {filterOptions.csp.map((opt) => (
            <option key={opt} value={opt}>
                {opt}
            </option>
            ))}
        </select>
        </div>

        {/* Genre */}
        <div className="flex-1 min-w-[140px]">
        <label className="block text-xs font-semibold text-primary-700 uppercase tracking-wide mb-1.5">
            Genre
        </label>
        <select
            value={filters.genre}
            onChange={(e) => updateFilters({ genre: e.target.value })}
            className="select"
        >
            {filterOptions.genre.map((opt) => (
            <option key={opt} value={opt}>
                {opt}
            </option>
            ))}
        </select>
        </div>

        {/* Âge */}
        <div className="flex-1 min-w-[200px]">
        <label className="block text-xs font-semibold text-primary-700 uppercase tracking-wide mb-1.5">
            Tranche d'âge
        </label>
        <div className="flex items-center gap-2">
            <input
            type="range"
            min={filterOptions.ageRange.min}
            max={filterOptions.ageRange.max}
            defaultValue={filterOptions.ageRange.max}
            onChange={(e) =>
                updateFilters({
                ageRange: [filterOptions.ageRange.min, parseInt(e.target.value)],
                })
            }
            className="flex-1 accent-primary-500"
            />
            <span className="text-sm font-medium text-slate-700 min-w-[60px] text-right">
            ≤ {filterOptions.ageRange.max} ans
            </span>
        </div>
        </div>

        {/* Reset + Effectif */}
        <div className="flex items-center gap-3 ml-auto">
        <button
            onClick={handleReset}
            className="btn-secondary gap-1.5 text-xs px-3 py-2"
            title="Réinitialiser les filtres"
        >
            <RefreshCw className="w-3.5 h-3.5" />
            Reset
        </button>

        <div className="flex items-center gap-2 px-3 py-2 bg-primary-50 rounded-lg border border-primary-100">
            <span className="text-xs text-primary-700 uppercase tracking-wide font-semibold">
            Effectif
            </span>
            <span className="text-lg font-bold text-primary-600 font-mono">
            {formatNumber(metrics?.demographics?.total || 0)}
            </span>
        </div>
        </div>
    </div>
    </div>
)
}