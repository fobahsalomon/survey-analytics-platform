import { useMemo } from 'react'
import { 
Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, 
ResponsiveContainer, Legend 
} from 'recharts'
import { formatNumber } from '../../utils/formatters'
import { COLORS } from '../../utils/colors'

export default function RadarChartComponent({ scores, dimensions }) {
const chartData = useMemo(() => {
    if (!scores || !dimensions) return []
    
    return dimensions.map(({ key, label }) => {
    const score = scores[key]
    return {
        subject: label,
        value: score?.pct || 0,
        fullMark: 100,
    }
    })
}, [scores, dimensions])

return (
    <div className="card">
    <ResponsiveContainer width="100%" height={400}>
        <RadarChart 
        cx="50%" 
        cy="50%" 
        outerRadius="80%" 
        data={chartData}
        >
        <PolarGrid 
            gridType="circle" 
            stroke="#edf5fd" 
            strokeDasharray="3 3"
        />
        <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fill: '#0f2340', fontSize: 10, fontWeight: 500 }}
            tickSize={0}
        />
        <PolarRadiusAxis 
            angle={90} 
            domain={[0, 100]} 
            tick={{ fill: '#6b88a8', fontSize: 9 }}
            axisLine={false}
            tickCount={5}
            tickFormatter={(v) => `${v}%`}
        />
        
        {/* Ligne de référence à 50% */}
        <Radar
            name="Référence 50%"
            dataKey={() => 50}
            stroke="rgba(249, 115, 22, 0.4)"
            strokeWidth={1.5}
            strokeDasharray="4 4"
            fill="none"
            dot={false}
        />
        
        {/* Données réelles */}
        <Radar
            name="Niveau élevé"
            dataKey="value"
            stroke={COLORS.primary[600]}
            strokeWidth={2.5}
            fill="rgba(56, 163, 232, 0.12)"
            fillOpacity={0.8}
            dot={{ 
            fill: COLORS.primary[600], 
            stroke: 'white', 
            strokeWidth: 2, 
            r: 4 
            }}
            activeDot={{ r: 6, stroke: 'white', strokeWidth: 2 }}
        />
        
        <Legend 
            verticalAlign="top" 
            height={36}
            formatter={(value) => (
            <span style={{ color: '#0f2340', fontSize: 11, fontWeight: 500 }}>{value}</span>
            )}
        />
        </RadarChart>
    </ResponsiveContainer>
    </div>
)
}