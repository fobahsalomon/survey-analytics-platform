import { useContext } from 'react'
import AnalysisContext from '../contexts/AnalysisContext'

/**
 * Hook personnalisé pour accéder au contexte d'analyse
 * @returns {Object} Contexte d'analyse complet
 */
export function useAnalysis() {
const context = useContext(AnalysisContext)

if (!context) {
    throw new Error('useAnalysis doit être utilisé dans un AnalysisProvider')
}

return {
    // État
    state: context.state,
    
    // Actions
    selectQuestionnaire: context.selectQuestionnaire,
    runAnalysis: context.runAnalysis,
    updateFilters: context.updateFilters,
    reset: context.reset,
    downloadReport: context.downloadReport,
    downloadFigure: context.downloadFigure,
    
    // États dérivés pratiques
    isLoading: context.state.isLoading,
    error: context.state.error,
    hasData: !!context.state.metrics,
    questionnaireType: context.state.selectedQuestionnaire,
    metrics: context.state.metrics,
    filters: context.state.filters,
}
}

export default useAnalysis