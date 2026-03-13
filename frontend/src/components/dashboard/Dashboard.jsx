import { useState, useMemo } from 'react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/Tabs'
import FilterBar from '../layout/FilterBar'
import KPICard from './KPICard'
import GaugeCard from './GaugeCard'
import QuadrantChart from './QuadrantChart'
import MappScatter from './MappScatter'
import RadarChart from './RadarChart'
import BarChartViewer from './BarChartViewer'
import { useAnalysis } from '../../hooks/useAnalysis'
import { formatNumber, formatPercent } from '../../utils/formatters'
import { RH_DIMENSIONS } from '../../utils/constants'

export default function Dashboard() {
const { state, updateFilters } = useAnalysis()
const { metrics, filters } = state
const [activeTab, setActiveTab] = useState('overview')

// Appliquer les filtres aux données (simulé - en prod, filtrer côté backend)
const filteredData = useMemo(() => {
    if (!metrics) return null
    
    // Ici on retournerait les données filtrées
    // Pour l'exemple, on retourne les metrics telles quelles
    return metrics
}, [metrics, filters])

if (!filteredData) {
    return (
    <div className="text-center py-12">
        <p className="text-muted">Aucune donnée à afficher</p>
    </div>
    )
}

const { demographics, lifestyle, quadrants, strain_prevalence, stress_indicators, rh_scores } = filteredData

return (
    <div className="space-y-6">
    {/* Barre de filtres */}
    <FilterBar availableFilters={{}} />

    {/* Tabs */}
    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-6">
        <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
        <TabsTrigger value="stress">Stress & Autonomie</TabsTrigger>
        </TabsList>

        {/* TAB 1: Vue d'ensemble */}
        <TabsContent value="overview" className="space-y-6">
        {/* Démographie */}
        <section>
            <h3 className="section-title">Effectif total — Données démographiques</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <KPICard
                value={demographics?.total || 0}
                label="Effectif total"
                icon="users"
                color="primary"
            />
            <KPICard
                value={demographics?.men?.pct || 0}
                label="Hommes"
                suffix="%"
                subtitle={formatNumber(demographics?.men?.n)}
                icon="male"
                color="primary"
            />
            <KPICard
                value={demographics?.women?.pct || 0}
                label="Femmes"
                suffix="%"
                subtitle={formatNumber(demographics?.women?.n)}
                icon="female"
                color="secondary"
            />
            <KPICard
                value={demographics?.avg_age || 0}
                label="Âge moyen"
                suffix=" ans"
                icon="calendar"
                color="secondary"
            />
            </div>
        </section>

        {/* Modes de vie */}
        <section>
            <h3 className="section-title">Indicateurs de modes de vie</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <KPICard
                value={lifestyle?.sedentarity?.pct || 0}
                label="Sédentarité"
                suffix="%"
                variant="lifestyle"
                threshold={35}
            />
            <KPICard
                value={lifestyle?.alcohol?.pct || 0}
                label="Alcool"
                suffix="%"
                variant="lifestyle"
                threshold={35}
            />
            <KPICard
                value={lifestyle?.tobacco?.pct || 0}
                label="Tabagisme"
                suffix="%"
                variant="lifestyle"
                threshold={35}
            />
            <KPICard
                value={lifestyle?.chronic?.pct || 0}
                label="Maladie chronique"
                suffix="%"
                variant="lifestyle"
                threshold={35}
            />
            <KPICard
                value={lifestyle?.overweight?.pct || 0}
                label="Surpoids & Obésité"
                suffix="%"
                variant="lifestyle"
                threshold={35}
            />
            </div>
        </section>

        {/* Explorateur démographique */}
        <section>
            <h3 className="section-title">Exploration des données démographiques</h3>
            <BarChartViewer data={filteredData} />
        </section>
        </TabsContent>

        {/* TAB 2: Stress & Autonomie */}
        <TabsContent value="stress" className="space-y-6">
        {/* KPIs de stress */}
        <section>
            <h3 className="section-title">Indicateurs clés de stress au travail</h3>
            <div className="grid md:grid-cols-3 gap-6">
            <GaugeCard
                value={stress_indicators?.autonomy?.pct || 0}
                label="Autonomie décisionnelle"
                sublabel="Flexibilité et contrôle perçus"
                isFavorable={true}
            />
            <GaugeCard
                value={stress_indicators?.workload?.pct || 0}
                label="Charge mentale perçue"
                sublabel="Intensité de la demande psychologique"
                isFavorable={false}
            />
            <GaugeCard
                value={stress_indicators?.social_support?.pct || 0}
                label="Cohésion d'équipe"
                sublabel="Soutien social collègues & management"
                isFavorable={true}
            />
            </div>
        </section>

        {/* Quadrants Karasek */}
        <section>
            <h3 className="section-title">Répartition par quadrant Karasek</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <KPICard
                value={quadrants?.Actif?.pct || 0}
                label="Actif"
                suffix="%"
                subtitle={formatNumber(quadrants?.Actif?.count)}
                variant="zone"
                color="#22c55e"
            />
            <KPICard
                value={quadrants?.Detendu?.pct || 0}
                label="Détendu"
                suffix="%"
                subtitle={formatNumber(quadrants?.Detendu?.count)}
                variant="zone"
                color="#38a3e8"
            />
            <KPICard
                value={quadrants?.Tendu?.pct || 0}
                label="Tendu"
                suffix="%"
                subtitle={formatNumber(quadrants?.Tendu?.count)}
                variant="zone"
                color="#ef4444"
            />
            <KPICard
                value={quadrants?.Passif?.pct || 0}
                label="Passif"
                suffix="%"
                subtitle={formatNumber(quadrants?.Passif?.count)}
                variant="zone"
                color="#94a3b8"
            />
            </div>
            <QuadrantChart data={quadrants} />
        </section>

        {/* Grille MAPP */}
        <section>
            <h3 className="section-title">Grille MAPP du Stress</h3>
            <p className="text-muted text-sm mb-4">
            Chaque point représente un agent. Les axes délimitent les zones du quadrant Karasek.
            </p>
            <MappScatter data={filteredData} />
        </section>

        {/* Prévalence RPS */}
        <section>
            <h3 className="section-title">Prévalence des RPS</h3>
            <div className="grid md:grid-cols-2 gap-4">
            <KPICard
                value={strain_prevalence?.Job_strain?.pct || 0}
                label="Job Strain"
                suffix="%"
                subtitle={`n=${strain_prevalence?.Job_strain?.n || 0}`}
                variant="strain"
                valueKey="Job_strain"
            />
            <KPICard
                value={strain_prevalence?.Iso_strain?.pct || 0}
                label="Iso-Strain"
                suffix="%"
                subtitle={`n=${strain_prevalence?.Iso_strain?.n || 0}`}
                variant="strain"
                valueKey="Iso_strain"
            />
            </div>
        </section>

        {/* Radar RH */}
        <section>
            <h3 className="section-title">Satisfaction organisationnelle</h3>
            <p className="text-muted text-sm mb-4">
            % de collaborateurs avec un niveau élevé de satisfaction par dimension
            </p>
            <div className="grid lg:grid-cols-[2fr_1fr] gap-6">
            <RadarChart scores={rh_scores} dimensions={RH_DIMENSIONS} />
            
            {/* Légende détaillée */}
            <div className="card">
                <h4 className="font-semibold text-slate-700 mb-4">Détail par dimension</h4>
                <div className="space-y-3">
                {RH_DIMENSIONS.map(({ key, label }) => {
                    const score = rh_scores?.[key]
                    const pct = score?.pct || 0
                    const n = score?.n || 0
                    const color = pct > 50 ? '#22c55e' : pct > 35 ? '#f59e0b' : '#ef4444'
                    
                    return (
                    <div key={key} className="space-y-1.5">
                        <div className="flex justify-between text-sm">
                        <span className="text-slate-600">{label}</span>
                        <span className="font-semibold" style={{ color }}>
                            {formatPercent(pct)} <span className="text-muted font-normal">({n})</span>
                        </span>
                        </div>
                        <div className="progress-track">
                        <div 
                            className="progress-fill"
                            style={{ 
                            width: `${pct}%`, 
                            backgroundColor: color,
                            transitionDelay: '100ms'
                            }}
                            data-target={pct}
                        />
                        </div>
                    </div>
                    )
                })}
                </div>
            </div>
            </div>
        </section>
        </TabsContent>
    </Tabs>
    </div>
)
}