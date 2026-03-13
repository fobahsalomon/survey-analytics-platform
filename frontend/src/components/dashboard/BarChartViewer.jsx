import { useState, useMemo } from 'react'
import { 
BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, 
ResponsiveContainer, Cell, Legend 
} from 'recharts'
import { DEMO_VARIABLES, CROSS_TAB_VARIABLES } from '../../utils/constants'
import { formatNumber, smartCapitalize } from '../../utils/formatters'
import { COLORS } from '../../utils/colors'

export default function BarChartViewer({ data }) {
const [selectedVar, setSelectedVar] = useState('Genre')
const [crossVar, setCrossVar] = useState(null)

// Filtrer les variables disponibles selon les colonnes présentes
const availableVars = useMemo(() => {
    if (!data?.rows?.[0]) return []
    const columns = Object.keys(data.rows[0])
    return DEMO_VARIABLES.filter(v => columns.includes(v.key))
}, [data])

const availableCross = useMemo(() => {
    if (!data?.rows?.[0]) return [{ key: null, label: 'Aucun croisement' }]
    const columns = Object.keys(data.rows[0])
    return CROSS_TAB_VARIABLES.filter(v => v.key === null || columns.includes(v.key))
}, [data])

// Préparer les données du graphique
const chartData = useMemo(() => {
    if (!data?.rows || !selectedVar) return []
    
    const rows = data.rows
    
    if (crossVar) {
    // Graphique empilé
    const crossValues = [...new Set(rows.map(r => r[crossVar]).filter(Boolean))]
    const mainValues = [...new Set(rows.map(r => r[selectedVar]).filter(Boolean))]
    
    return mainValues.map(mainVal => {
        const entry = { name: smartCapitalize(mainVal) }
        
        crossValues.forEach(crossVal => {
        const count = rows.filter(r => 
            r[selectedVar] === mainVal && r[crossVar] === crossVal
        ).length
        const total = rows.filter(r => r[selectedVar] === mainVal).length
        entry[smartCapitalize(crossVal)] = total > 0 ? (count / total * 100) : 0
        })
        
        return entry
    })
    } else {
    // Graphique simple
    const values = [...new Set(rows.map(r => r[selectedVar]).filter(Boolean))]
    
    return values.map(val => {
        const count = rows.filter(r => r[selectedVar] === val).length
        return {
        name: smartCapitalize(val),
        value: (count / rows.length * 100).toFixed(1),
        count,
        }
    })
    }
}, [data, selectedVar, crossVar])

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.[0]) return null
    
    if (crossVar) {
    // Tooltip pour stacked bar
    return (
        <div className="bg-white border border-border rounded-lg shadow-lg p-3 text-sm">
        <p className="font-semibold text-slate-800 mb-2">{label}</p>
        {payload.map((p, i) => (
            <p key={i} className="flex justify-between gap-4">
            <span style={{ color: p.color }}>{p.name}:</span>
            <span className="font-medium">{formatNumber(p.value, 1)}%</span>
            </p>
        ))}
        </div>
    )
    }
    
    // Tooltip pour bar simple
    const { value, count } = payload[0].payload
    return (
    <div className="bg-white border border-border rounded-lg shadow-lg p-3 text-sm">
        <p className="font-semibold text-slate-800">{label}</p>
        <p className="text-primary-600 font-bold">{formatNumber(value, 1)}%</p>
        <p className="text-muted">n = {formatNumber(count)}</p>
    </div>
    )
}

return (
    <div className="card">
    {/* Sélecteurs */}
    <div className="flex flex-wrap gap-4 mb-4">
        <div className="flex-1 min-w-[200px]">
        <label className="block text-xs font-semibold text-primary-700 uppercase tracking-wide mb-1.5">
            Variable
        </label>
        <select
            value={selectedVar}
            onChange={(e) => setSelectedVar(e.target.value)}
            className="select"
        >
            {availableVars.map(v => (
            <option key={v.key} value={v.key}>{v.label}</option>
            ))}
        </select>
        </div>
        
        <div className="flex-1 min-w-[200px]">
        <label className="block text-xs font-semibold text-primary-700 uppercase tracking-wide mb-1.5">
            Croiser avec
        </label>
        <select
            value={crossVar || ''}
            onChange={(e) => setCrossVar(e.target.value || null)}
            className="select"
        >
            {availableCross.map(v => (
            <option key={v.key || 'none'} value={v.key || ''}>
                {v.label}
            </option>
            ))}
        </select>
        </div>
    </div>

    {/* Graphique */}
    {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
        <BarChart 
            data={chartData}
            layout={crossVar ? "horizontal" : "vertical"}
            margin={{ top: 10, right: crossVar ? 100 : 40, left: crossVar ? 80 : 20, bottom: 10 }}
        >
            <CartesianGrid strokeDasharray="4 4" stroke="#edf5fd" />
            <XAxis 
            type={crossVar ? "number" : "category"}
            domain={crossVar ? [0, 100] : undefined}
            tick={{ fill: '#6b88a8', fontSize: 10 }}
            axisLine={{ stroke: '#d6e8f7' }}
            label={crossVar ? { 
                value: 'Pourcentage (%)', 
                position: 'bottom', 
                fill: '#6b88a8',
                fontSize: 10,
            } : undefined}
            />
            <YAxis 
            type={crossVar ? "category" : "number"}
            domain={crossVar ? undefined : [0, 120]}
            tick={{ fill: '#0f2340', fontSize: 10, fontWeight: 500 }}
            axisLine={false}
            tickLine={false}
            width={crossVar ? 80 : undefined}
            />
            <Tooltip content={<CustomTooltip />} />
            
            {crossVar ? (
            // Stacked bars
            <>
                {Object.keys(chartData[0])
                .filter(k => k !== 'name')
                .map((key, i) => (
                    <Bar 
                    key={key}
                    dataKey={key} 
                    stackId="a"
                    radius={[0, 8, 8, 0]}
                    barSize={28}
                    >
                    {chartData.map((_, index) => (
                        <Cell 
                        key={`cell-${index}`} 
                        fill={COLORS.categorical[i % COLORS.categorical.length]} 
                        />
                    ))}
                    </Bar>
                ))
                }
                <Legend 
                verticalAlign="right" 
                align="right"
                layout="vertical"
                wrapperStyle={{ fontSize: 10 }}
                formatter={(value) => (
                    <span style={{ color: '#0f2340', fontSize: 10 }}>{value}</span>
                )}
                />
            </>
            ) : (
            // Simple bars
            <Bar 
                dataKey="value" 
                radius={[0, 8, 8, 0]} 
                barSize={32}
                fill={COLORS.primary[500]}
            >
                {chartData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS.categorical[index % COLORS.categorical.length]} />
                ))}
            </Bar>
            )}
        </BarChart>
        </ResponsiveContainer>
    ) : (
        <div className="flex items-center justify-center h-[300px]">
        <p className="text-muted">Données insuffisantes pour ce croisement</p>
        </div>
    )}
    </div>
)
}