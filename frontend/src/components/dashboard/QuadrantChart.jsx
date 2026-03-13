import { useMemo } from 'react'
import { 
BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, 
ResponsiveContainer, Cell, LabelList 
} from 'recharts'
import { formatNumber } from '../../utils/formatters'
import { COLORS } from '../../utils/colors'

const QUADRANT_ORDER = ['Actif', 'Detendu', 'Tendu', 'Passif']
const QUADRANT_LABELS = {
Actif: 'Actif',
Detendu: 'Détendu',
Tendu: 'Tendu',
Passif: 'Passif',
}

export default function QuadrantChart({ data }) {
const chartData = useMemo(() => {
    if (!data) return []
    
    return QUADRANT_ORDER
    .filter(q => data[q])
    .map(q => ({
        name: QUADRANT_LABELS[q] || q,
        value: data[q].pct,
        count: data[q].count,
        fill: COLORS.karasek[q.toLowerCase()] || COLORS.muted,
    }))
}, [data])

const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.[0]) return null
    
    const { name, value, count } = payload[0].payload
    
    return (
    <div className="bg-white border border-border rounded-lg shadow-lg p-3 text-sm">
        <p className="font-semibold text-slate-800">{name}</p>
        <p className="text-primary-600 font-bold">{formatNumber(value, 1)}%</p>
        <p className="text-muted">n = {formatNumber(count)}</p>
    </div>
    )
}

return (
    <div className="card">
    <ResponsiveContainer width="100%" height={280}>
        <BarChart 
        data={chartData} 
        layout="vertical"
        margin={{ top: 10, right: 40, left: 20, bottom: 10 }}
        >
        <CartesianGrid strokeDasharray="4 4" stroke="#edf5fd" horizontal={false} />
        <XAxis 
            type="number" 
            domain={[0, 120]} 
            tick={{ fill: '#6b88a8', fontSize: 11 }}
            axisLine={{ stroke: '#d6e8f7' }}
            label={{ 
            value: 'Pourcentage (%)', 
            position: 'bottom', 
            offset: 0,
            fill: '#6b88a8',
            fontSize: 11,
            }}
        />
        <YAxis 
            type="category" 
            dataKey="name" 
            tick={{ fill: '#0f2340', fontSize: 12, fontWeight: 500 }}
            axisLine={false}
            tickLine={false}
            width={80}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(56, 163, 232, 0.05)' }} />
        
        <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={32} animationDuration={800}>
            {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
            <LabelList 
            dataKey="value" 
            position="right" 
            formatter={(v) => `${formatNumber(v, 1)}%`}
            fill="#6b88a8"
            fontSize={11}
            fontWeight={500}
            />
        </Bar>
        </BarChart>
    </ResponsiveContainer>
    </div>
)
}