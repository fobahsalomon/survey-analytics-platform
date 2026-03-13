import { Routes, Route, Navigate } from 'react-router-dom'
import { useAnalysis } from './hooks/useAnalysis'
import QuestionnaireSelector from './components/upload/QuestionnaireSelector'
import FileUploader from './components/upload/FileUploader'
import Dashboard from './components/dashboard/Dashboard'
import Header from './components/layout/Header'
import LoadingSpinner from './components/layout/LoadingSpinner'

function App() {
const { state, isLoading, error } = useAnalysis()

if (isLoading) {
    return (
    <div className="min-h-screen flex items-center justify-center bg-background">
        <LoadingSpinner size="lg" />
    </div>
    )
}

if (error) {
    return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <div className="card max-w-md text-center">
        <h2 className="text-xl font-semibold text-danger mb-2">Erreur</h2>
        <p className="text-muted mb-4">{error}</p>
        <button 
            onClick={() => window.location.reload()}
            className="btn-primary"
        >
            Réessayer
        </button>
        </div>
    </div>
    )
}

return (
    <div className="min-h-screen flex flex-col">
    <Header />
    
    <main className="flex-1 container mx-auto px-4 py-6 max-w-7xl">
        <Routes>
        <Route 
            path="/" 
            element={
            !state.selectedQuestionnaire 
                ? <QuestionnaireSelector /> 
                : !state.data 
                ? <FileUploader /> 
                : <Navigate to="/dashboard" replace />
            } 
        />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    </main>
    </div>
)
}

export default App