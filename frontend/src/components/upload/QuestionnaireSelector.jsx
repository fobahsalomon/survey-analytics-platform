import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, Activity, HeartPulse, ArrowRight } from 'lucide-react'
import { useAnalysis } from '../../hooks/useAnalysis'
import { 
QUESTIONNAIRE_TYPES, 
QUESTIONNAIRE_LABELS, 
QUESTIONNAIRE_DESCRIPTIONS 
} from '../../utils/constants'

export default function QuestionnaireSelector() {
const [selected, setSelected] = useState(null)
const { selectQuestionnaire } = useAnalysis()
const navigate = useNavigate()

const questionnaires = [
    {
    type: QUESTIONNAIRE_TYPES.KARASEK,
    icon: Activity,
    color: 'from-blue-500 to-cyan-500',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    hoverColor: 'hover:border-blue-400 hover:shadow-blue-500/20',
    },
    {
    type: QUESTIONNAIRE_TYPES.QVT,
    icon: HeartPulse,
    color: 'from-emerald-500 to-teal-500',
    bgColor: 'bg-emerald-50',
    borderColor: 'border-emerald-200',
    hoverColor: 'hover:border-emerald-400 hover:shadow-emerald-500/20',
    },
    {
    type: QUESTIONNAIRE_TYPES.MBI,
    icon: FileText,
    color: 'from-violet-500 to-purple-500',
    bgColor: 'bg-violet-50',
    borderColor: 'border-violet-200',
    hoverColor: 'hover:border-violet-400 hover:shadow-violet-500/20',
    },
]

const handleSelect = (type) => {
    setSelected(type)
    selectQuestionnaire(type)
}

const handleContinue = () => {
    if (selected) {
    navigate('/')
    }
}

return (
    <div className="max-w-4xl mx-auto py-12">
    {/* Header */}
    <div className="text-center mb-12">
        <h2 className="font-serif text-3xl font-semibold italic text-slate-800 mb-3">
        Sélectionnez votre <span className="text-primary-600">questionnaire</span>
        </h2>
        <p className="text-muted text-lg max-w-2xl mx-auto">
        Choisissez le type d'analyse que vous souhaitez réaliser sur vos données
        </p>
    </div>

    {/* Cards */}
    <div className="grid md:grid-cols-3 gap-6 mb-8">
        {questionnaires.map(({ type, icon: Icon, color, bgColor, borderColor, hoverColor }) => {
        const isSelected = selected === type
        
        return (
            <button
            key={type}
            onClick={() => handleSelect(type)}
            className={`
                relative card text-left cursor-pointer transition-all duration-300
                border-2 ${isSelected ? `${borderColor} ring-2 ring-primary-500/20` : 'border-border'}
                ${hoverColor}
                ${isSelected ? 'bg-primary-50/50' : ''}
                group
            `}
            >
            {/* Badge sélection */}
            {isSelected && (
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center shadow-lg">
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
                </div>
            )}
            
            {/* Icone */}
            <div className={`
                w-14 h-14 rounded-2xl bg-gradient-to-br ${color} 
                flex items-center justify-center mb-4 shadow-lg
                group-hover:scale-105 transition-transform duration-300
            `}>
                <Icon className="w-7 h-7 text-white" />
            </div>
            
            {/* Titre */}
            <h3 className="font-semibold text-lg text-slate-800 mb-2">
                {QUESTIONNAIRE_LABELS[type]}
            </h3>
            
            {/* Description */}
            <p className="text-sm text-muted leading-relaxed">
                {QUESTIONNAIRE_DESCRIPTIONS[type]}
            </p>
            
            {/* Dimensions */}
            <div className="mt-4 flex flex-wrap gap-1.5">
                {type === QUESTIONNAIRE_TYPES.KARASEK && (
                <>
                    <span className="badge badge-info text-xs">Demande</span>
                    <span className="badge badge-info text-xs">Contrôle</span>
                    <span className="badge badge-info text-xs">Soutien</span>
                </>
                )}
                {type === QUESTIONNAIRE_TYPES.QVT && (
                <>
                    <span className="badge badge-info text-xs">Environnement</span>
                    <span className="badge badge-info text-xs">Relations</span>
                    <span className="badge badge-info text-xs">Développement</span>
                </>
                )}
                {type === QUESTIONNAIRE_TYPES.MBI && (
                <>
                    <span className="badge badge-info text-xs">Épuisement</span>
                    <span className="badge badge-info text-xs">Dépersonnalisation</span>
                    <span className="badge badge-info text-xs">Accomplissement</span>
                </>
                )}
            </div>
            </button>
        )
        })}
    </div>

    {/* Bouton Continuer */}
    <div className="text-center">
        <button
        onClick={handleContinue}
        disabled={!selected}
        className={`
            btn gap-2 px-8 py-3 text-base
            ${selected 
            ? 'btn-primary' 
            : 'bg-slate-200 text-slate-400 cursor-not-allowed hover:bg-slate-200'
            }
        `}
        >
        Continuer
        <ArrowRight className="w-4 h-4" />
        </button>
        
        {selected && (
        <p className="mt-3 text-sm text-muted">
            Sélectionné: <span className="font-medium text-slate-700">{QUESTIONNAIRE_LABELS[selected]}</span>
        </p>
        )}
    </div>
    </div>
)
}