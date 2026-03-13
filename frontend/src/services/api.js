import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
baseURL: API_BASE_URL,
headers: {
    'Content-Type': 'application/json',
},
timeout: 120000, // 2 minutes pour les analyses longues
})

// Interceptor pour ajouter le token si nécessaire (futur)
api.interceptors.request.use((config) => {
const token = localStorage.getItem('token')
if (token) {
    config.headers.Authorization = `Bearer ${token}`
}
return config
})

// Interceptor pour gérer les erreurs globales
api.interceptors.response.use(
(response) => response,
(error) => {
    if (error.response) {
    // Erreur côté serveur
    console.error('API Error:', error.response.data)
    return Promise.reject(new Error(error.response.data.detail || 'Erreur serveur'))
    } else if (error.request) {
    // Pas de réponse du serveur
    console.error('No response from server')
    return Promise.reject(new Error('Impossible de contacter le serveur'))
    }
    return Promise.reject(error)
}
)

export const questionnaireAPI = {
// Liste des questionnaires disponibles
listQuestionnaires: async () => {
    const { data } = await api.get('/questionnaires')
    return data
},

// Détails d'un questionnaire
getQuestionnaireInfo: async (type) => {
    const { data } = await api.get(`/questionnaires/${type}`)
    return data
},

// Lancer une analyse
startAnalysis: async (questionnaireType, file) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const { data } = await api.post(`/analyze/${questionnaireType}`, formData, {
    headers: {
        'Content-Type': 'multipart/form-data',
    },
    })
    return data.data
},

// Récupérer les résultats d'une session
getResults: async (questionnaireType, sessionId) => {
    const { data } = await api.get(`/results/${questionnaireType}/${sessionId}`)
    return data.data
},

// Télécharger le rapport Word
downloadReport: async (questionnaireType, sessionId, filename = 'rapport_karasek.docx') => {
    const response = await api.get(
    `/reports/${questionnaireType}/${sessionId}/${filename}`,
    { responseType: 'blob' }
    )
    
    // Créer un lien de téléchargement
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
},

// Télécharger une figure
downloadFigure: async (questionnaireType, sessionId, figureName) => {
    const response = await api.get(
    `/figures/${questionnaireType}/${sessionId}/${figureName}`,
    { responseType: 'blob' }
    )
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', figureName)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
},

// Vérifier la santé de l'API
healthCheck: async () => {
    const { data } = await api.get('/health')
    return data
},
}

export default api