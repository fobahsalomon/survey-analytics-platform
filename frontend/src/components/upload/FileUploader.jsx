import { useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, File, X, AlertCircle, CheckCircle2 } from 'lucide-react'
import { useAnalysis } from '../../hooks/useAnalysis'
import { formatNumber } from '../../utils/formatters'
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from '../../utils/constants'

export default function FileUploader() {
const [file, setFile] = useState(null)
const [isDragging, setIsDragging] = useState(false)
const [uploadStatus, setUploadStatus] = useState(null) // 'success' | 'error' | null
const [errorMessage, setErrorMessage] = useState('')

const { runAnalysis, isLoading } = useAnalysis()
const navigate = useNavigate()
const fileInputRef = useRef(null)

// Validation du fichier
const validateFile = (file) => {
    const maxSize = 50 * 1024 * 1024 // 50 MB
    const allowedTypes = ['text/csv', 'application/csv', 'application/vnd.ms-excel']
    const allowedExtensions = ['.csv']
    
    if (file.size > maxSize) {
    return { valid: false, error: ERROR_MESSAGES.FILE_TOO_LARGE }
    }
    
    const ext = '.' + file.name.split('.').pop().toLowerCase()
    if (!allowedExtensions.includes(ext)) {
    return { valid: false, error: ERROR_MESSAGES.INVALID_FORMAT }
    }
    
    return { valid: true }
}

// Gestion du drop
const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
}, [])

const handleDragIn = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
}, [])

const handleDragOut = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
}, [])

const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
    handleFileSelect(droppedFile)
    }
}, [])

// Gestion de la sélection de fichier
const handleFileSelect = (selectedFile) => {
    setUploadStatus(null)
    setErrorMessage('')
    
    const validation = validateFile(selectedFile)
    if (!validation.valid) {
    setUploadStatus('error')
    setErrorMessage(validation.error)
    setFile(null)
    return
    }
    
    setFile(selectedFile)
    setUploadStatus('success')
}

// Supprimer le fichier sélectionné
const handleRemoveFile = () => {
    setFile(null)
    setUploadStatus(null)
    setErrorMessage('')
    if (fileInputRef.current) {
    fileInputRef.current.value = ''
    }
}

// Lancer l'analyse
const handleAnalyze = async () => {
    if (!file) return
    
    try {
    await runAnalysis(file)
    setUploadStatus('success')
    navigate('/dashboard')
    } catch (error) {
    setUploadStatus('error')
    setErrorMessage(error.message || ERROR_MESSAGES.ANALYSIS_FAILED)
    }
}

return (
    <div className="max-w-2xl mx-auto py-8">
    {/* Header */}
    <div className="text-center mb-8">
        <h2 className="font-serif text-2xl font-semibold italic text-slate-800 mb-2">
        Importez vos <span className="text-primary-600">données</span>
        </h2>
        <p className="text-muted">
        Téléversez votre fichier CSV pour lancer l'analyse
        </p>
    </div>

    {/* Zone de drop */}
    <div
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
        card cursor-pointer transition-all duration-300 min-h-[200px]
        flex flex-col items-center justify-center gap-4
        ${isDragging 
            ? 'border-2 border-dashed border-primary-400 bg-primary-50/50 scale-[1.02]' 
            : 'border-2 border-dashed border-border hover:border-primary-300 hover:bg-slate-50/50'
        }
        ${uploadStatus === 'error' ? 'border-danger/50 bg-danger/5' : ''}
        ${uploadStatus === 'success' && file ? 'border-success/50 bg-success/5' : ''}
        `}
    >
        <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        onChange={(e) => e.target.files[0] && handleFileSelect(e.target.files[0])}
        className="hidden"
        />
        
        {file ? (
        // Fichier sélectionné
        <div className="flex items-center gap-4 w-full max-w-md">
            <div className="w-12 h-12 rounded-xl bg-success/10 flex items-center justify-center flex-shrink-0">
            <File className="w-6 h-6 text-success" />
            </div>
            
            <div className="flex-1 min-w-0">
            <p className="font-medium text-slate-800 truncate">{file.name}</p>
            <p className="text-sm text-muted">
                {formatNumber(file.size / 1024, 1)} Ko
            </p>
            </div>
            
            <button
            onClick={(e) => {
                e.stopPropagation()
                handleRemoveFile()
            }}
            className="p-2 rounded-lg hover:bg-slate-100 text-muted hover:text-danger transition-colors"
            title="Supprimer le fichier"
            >
            <X className="w-5 h-5" />
            </button>
        </div>
        ) : (
        // État vide
        <>
            <div className={`
            w-16 h-16 rounded-2xl flex items-center justify-center
            ${isDragging ? 'bg-primary-100' : 'bg-slate-100'}
            transition-colors duration-300
            `}>
            <Upload className={`w-8 h-8 ${isDragging ? 'text-primary-500' : 'text-muted'}`} />
            </div>
            
            <div className="text-center">
            <p className="font-medium text-slate-700">
                {isDragging ? 'Déposez votre fichier ici' : 'Glissez-déposez votre fichier CSV'}
            </p>
            <p className="text-sm text-muted mt-1">
                ou <span className="text-primary-600 font-medium">parcourir</span>
            </p>
            </div>
            
            <p className="text-xs text-muted text-center max-w-xs">
            Formats supportés: .csv • Taille max: 50 Mo
            </p>
        </>
        )}
    </div>

    {/* Messages de statut */}
    {uploadStatus === 'error' && errorMessage && (
        <div className="mt-4 p-4 rounded-xl bg-danger/10 border border-danger/20 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
        <div>
            <p className="font-medium text-danger">Erreur</p>
            <p className="text-sm text-slate-600 mt-0.5">{errorMessage}</p>
        </div>
        </div>
    )}
    
    {uploadStatus === 'success' && file && !isLoading && (
        <div className="mt-4 p-4 rounded-xl bg-success/10 border border-success/20 flex items-start gap-3">
        <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
        <div>
            <p className="font-medium text-success">Fichier prêt</p>
            <p className="text-sm text-slate-600 mt-0.5">
            Cliquez sur "Lancer l'analyse" pour commencer
            </p>
        </div>
        </div>
    )}

    {/* Bouton d'action */}
    <div className="mt-8 text-center">
        <button
        onClick={handleAnalyze}
        disabled={!file || isLoading}
        className={`
            btn gap-2 px-8 py-3 text-base
            ${file && !isLoading
            ? 'btn-primary' 
            : 'bg-slate-200 text-slate-400 cursor-not-allowed hover:bg-slate-200'
            }
        `}
        >
        {isLoading ? (
            <>
            <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Analyse en cours...
            </>
        ) : (
            <>
            Lancer l'analyse
            </>
        )}
        </button>
    </div>

    {/* Aide */}
    <div className="mt-8 p-4 rounded-xl bg-slate-50 border border-border">
        <h4 className="font-medium text-slate-700 mb-2">📋 Format de fichier attendu</h4>
        <ul className="text-sm text-muted space-y-1">
        <li>• Fichier CSV encodé en UTF-8 ou Latin-1</li>
        <li>• Première ligne: en-têtes de colonnes</li>
        <li>• Questions Likert: valeurs numériques 1-4</li>
        <li>• Variables démographiques: Genre, Age, Direction, etc.</li>
        </ul>
    </div>
    </div>
)
}