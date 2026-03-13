import { useMemo, useEffect, useRef } from 'react'
import { clsx } from 'clsx'
import { 
Users, User, User2, Calendar, Activity, AlertTriangle, 
CheckCircle, XCircle, TrendingUp, TrendingDown 
} from 'lucide-react'
import { formatNumber } from '../../utils/formatters'
import { COLORS } from '../../utils/colors'

const ICONS = {
users: Users,
male: User,
female: User2,
calendar: Calendar,
activity: Activity,
warning: AlertTriangle,
success: CheckCircle,
error: XCircle,
up: TrendingUp,
down: TrendingDown,
}

export default function KPICard({
value,
label,
suffix = '',
prefix = '',
subtitle,
icon,
variant = 'default',
color = 'primary',
threshold,
className,
animate = true,
}) {
const valueRef = useRef(null)
const numValue = useMemo(() => {
    const num = parseFloat(value)
    return isNaN(num) ? 0 : num
}, [value])

// Déterminer la couleur selon le variant et la valeur
const getColor = () => {
    if (variant === 'lifestyle' && threshold !== undefined) {
    if (numValue < threshold) return COLORS.success
    if (numValue > threshold + 25) return COLORS.danger
    return COLORS.warning
    }
    if (variant === 'strain') {
    return numValue > 15 ? COLORS.danger : COLORS.success
    }
    if (variant === 'zone') {
    return color
    }
    return COLORS.primary[600]
}

const displayColor = getColor()

// Animation du compteur
useEffect(() => {
    if (!animate || !valueRef.current) return
    
    const target = numValue
    const duration = 600
    const start = performance.now()
    
    const easeOut = (t) => 1 - Math.pow(1 - t, 3)
    
    const animateCount = (now) => {
    const progress = Math.min(1, (now - start) / duration)
    const current = target * easeOut(progress)
    
    const decimals = suffix === '%' ? 1 : 0
    valueRef.current.textContent = 
        prefix + (decimals === 0 ? Math.round(current) : current.toFixed(decimals)) + suffix
    
    if (progress < 1) {
        requestAnimationFrame(animateCount)
    } else {
        valueRef.current.textContent = 
        prefix + (decimals === 0 ? Math.round(target) : target.toFixed(decimals)) + suffix
    }
    }
    
    requestAnimationFrame(animateCount)
}, [numValue, prefix, suffix, animate])

const Icon = icon ? ICONS[icon] : null

return (
    <div className={clsx(
    'card text-center relative overflow-hidden group',
    variant === 'lifestyle' && 'border-t-4 hover:-translate-y-0.5',
    variant === 'zone' && 'border-t-4',
    className
    )}
    style={variant === 'lifestyle' || variant === 'zone' ? { borderTopColor: displayColor } : {}}
    >
    {/* Icone optionnelle */}
    {Icon && (
        <div 
        className="w-10 h-10 rounded-xl mx-auto mb-3 flex items-center justify-center"
        style={{ backgroundColor: `${displayColor}15`, color: displayColor }}
        >
        <Icon className="w-5 h-5" />
        </div>
    )}
    
    {/* Label */}
    <span className="block text-xs font-semibold text-muted uppercase tracking-wide mb-1.5">
        {label}
    </span>
    
    {/* Valeur */}
    <div 
        ref={valueRef}
        className="text-3xl font-bold text-slate-800 font-mono tracking-tight"
        style={{ color: variant === 'default' ? undefined : displayColor }}
    >
        {prefix}{formatNumber(numValue, suffix === '%' ? 1 : 0)}{suffix}
    </div>
    
    {/* Sous-titre */}
    {subtitle && (
        <p className="mt-1.5 text-sm font-medium text-muted">
        {subtitle}
        </p>
    )}
    
    {/* Badge indicateur */}
    {variant === 'lifestyle' && threshold !== undefined && (
        <span className={clsx(
        'absolute top-3 right-3 badge text-xs',
        numValue < threshold ? 'badge-success' :
        numValue > threshold + 25 ? 'badge-danger' : 'badge-warning'
        )}>
        {numValue < threshold ? 'Bon' : numValue > threshold + 25 ? 'Alerte' : 'Moyen'}
        </span>
    )}
    </div>
)
}