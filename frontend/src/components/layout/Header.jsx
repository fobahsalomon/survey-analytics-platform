import { Link, useLocation } from 'react-router-dom'
import { Home, ArrowLeft, Download, RefreshCw } from 'lucide-react'
import { useAnalysis } from '../../hooks/useAnalysis'
import { QUESTIONNAIRE_LABELS } from '../../utils/constants'

export default function Header() {
  const { state, reset, downloadReport } = useAnalysis()
  const location = useLocation()
  const isDashboard = location.pathname === '/dashboard'
  const hasData = !!state.metrics

  return (
    <header className="bg-white border-b border-border sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-4 py-3 max-w-7xl">
        <div className="flex items-center justify-between">
          {/* Logo + Titre */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-lg group-hover:shadow-primary-500/25 transition-shadow">
              <span className="text-white font-serif font-bold text-lg">K</span>
            </div>
            <div>
              <h1 className="font-serif text-lg font-semibold italic text-slate-800">
                Karasek <span className="text-primary-600">Dashboard</span>
              </h1>
              <p className="text-xs text-muted uppercase tracking-wide font-medium">
                Analyse du bien-être au travail
              </p>
            </div>
          </Link>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {isDashboard && hasData && (
              <>
                <button
                  onClick={downloadReport}
                  className="btn-secondary gap-2 text-sm"
                  title="Télécharger le rapport Word"
                >
                  <Download className="w-4 h-4" />
                  <span className="hidden sm:inline">Rapport</span>
                </button>
                
                <button
                  onClick={reset}
                  className="btn-secondary gap-2 text-sm"
                  title="Nouvelle analyse"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span className="hidden sm:inline">Nouveau</span>
                </button>
              </>
            )}
            
            {!isDashboard && state.selectedQuestionnaire && (
              <Link to="/" className="btn-secondary gap-2 text-sm">
                <ArrowLeft className="w-4 h-4" />
                <span className="hidden sm:inline">Retour</span>
              </Link>
            )}
          </div>
        </div>

        {/* Badge questionnaire sélectionné */}
        {state.selectedQuestionnaire && (
          <div className="mt-2 flex items-center gap-2">
            <span className="text-xs text-muted uppercase tracking-wide">
              Questionnaire:
            </span>
            <span className="badge badge-info">
              {QUESTIONNAIRE_LABELS[state.selectedQuestionnaire]}
            </span>
            {state.sessionId && (
              <span className="text-xs text-muted font-mono">
                • Session: {state.sessionId}
              </span>
            )}
          </div>
        )}
      </div>
    </header>
  )
}