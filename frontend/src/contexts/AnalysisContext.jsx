import { createContext, useContext, useReducer, useCallback } from 'react'
import { questionnaireAPI } from '../services/api'
import { QUESTIONNAIRE_TYPES } from '../utils/constants'

// État initial
const initialState = {
  selectedQuestionnaire: null,
  data: null,
  metrics: null,
  sessionId: null,
  isLoading: false,
  error: null,
  filters: {
    direction: 'Tous',
    csp: 'Tous',
    genre: 'Tous',
    ageRange: null,
  },
}

// Types d'actions
const ActionTypes = {
  SET_QUESTIONNAIRE: 'SET_QUESTIONNAIRE',
  SET_DATA: 'SET_DATA',
  SET_METRICS: 'SET_METRICS',
  SET_SESSION: 'SET_SESSION',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_FILTERS: 'SET_FILTERS',
  RESET: 'RESET',
}

// Reducer
function analysisReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_QUESTIONNAIRE:
      return { ...state, selectedQuestionnaire: action.payload, data: null, metrics: null }
    
    case ActionTypes.SET_DATA:
      return { ...state, data: action.payload }
    
    case ActionTypes.SET_METRICS:
      return { ...state, metrics: action.payload }
    
    case ActionTypes.SET_SESSION:
      return { ...state, sessionId: action.payload }
    
    case ActionTypes.SET_LOADING:
      return { ...state, isLoading: action.payload }
    
    case ActionTypes.SET_ERROR:
      return { ...state, error: action.payload, isLoading: false }
    
    case ActionTypes.SET_FILTERS:
      return {
        ...state,
        filters: { ...state.filters, ...action.payload },
      }
    
    case ActionTypes.RESET:
      return { ...initialState }
    
    default:
      return state
  }
}

// Context
const AnalysisContext = createContext(null)

// Provider
export function AnalysisProvider({ children }) {
  const [state, dispatch] = useReducer(analysisReducer, initialState)

  // Sélectionner un questionnaire
  const selectQuestionnaire = useCallback((type) => {
    dispatch({ type: ActionTypes.SET_QUESTIONNAIRE, payload: type })
  }, [])

  // Lancer une analyse
  const runAnalysis = useCallback(async (file) => {
    if (!state.selectedQuestionnaire) {
      throw new Error('Aucun questionnaire sélectionné')
    }

    dispatch({ type: ActionTypes.SET_LOADING, payload: true })
    dispatch({ type: ActionTypes.SET_ERROR, payload: null })

    try {
      const result = await questionnaireAPI.startAnalysis(
        state.selectedQuestionnaire,
        file
      )

      dispatch({ type: ActionTypes.SET_DATA, payload: result })
      dispatch({ type: ActionTypes.SET_METRICS, payload: result.metrics })
      dispatch({ type: ActionTypes.SET_SESSION, payload: result.session_id })
      
      return result
    } catch (error) {
      dispatch({ type: ActionTypes.SET_ERROR, payload: error.message })
      throw error
    } finally {
      dispatch({ type: ActionTypes.SET_LOADING, payload: false })
    }
  }, [state.selectedQuestionnaire])

  // Mettre à jour les filtres
  const updateFilters = useCallback((filters) => {
    dispatch({ type: ActionTypes.SET_FILTERS, payload: filters })
  }, [])

  // Réinitialiser l'état
  const reset = useCallback(() => {
    dispatch({ type: ActionTypes.RESET })
  }, [])

  // Télécharger le rapport
  const downloadReport = useCallback(async () => {
    if (!state.sessionId || !state.selectedQuestionnaire) return
    
    await questionnaireAPI.downloadReport(
      state.selectedQuestionnaire,
      state.sessionId
    )
  }, [state.sessionId, state.selectedQuestionnaire])

  // Télécharger une figure
  const downloadFigure = useCallback(async (figureName) => {
    if (!state.sessionId || !state.selectedQuestionnaire) return
    
    await questionnaireAPI.downloadFigure(
      state.selectedQuestionnaire,
      state.sessionId,
      figureName
    )
  }, [state.sessionId, state.selectedQuestionnaire])

  const value = {
    state,
    selectQuestionnaire,
    runAnalysis,
    updateFilters,
    reset,
    downloadReport,
    downloadFigure,
    isLoading: state.isLoading,
    error: state.error,
  }

  return (
    <AnalysisContext.Provider value={value}>
      {children}
    </AnalysisContext.Provider>
  )
}

// Hook personnalisé
export function useAnalysis() {
  const context = useContext(AnalysisContext)
  if (!context) {
    throw new Error('useAnalysis must be used within an AnalysisProvider')
  }
  return context
}

export default AnalysisContext