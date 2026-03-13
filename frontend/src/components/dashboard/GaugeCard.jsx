import { useEffect, useRef, useMemo } from 'react'
import { clsx } from 'clsx'
import { COLORS } from '../../utils/colors'

export default function GaugeCard({
value,
label,
sublabel,
isFavorable = true,
className,
}) {
const fillRef = useRef(null)
const counterRef = useRef(null)

const numValue = useMemo(() => {
    const num = parseFloat(value)
    return isNaN(num) ? 0 : Math.max(0, Math.min(100, num))
}, [value])

// Déterminer la couleur et le badge
const { color, badgeClass, badgeText } = useMemo(() => {
    if (isFavorable) {
    return numValue > 50 
        ? { color: COLORS.success, badgeClass: 'badge-success', badgeText: 'Élevé' }
        : { color: COLORS.danger, badgeClass: 'badge-danger', badgeText: 'Faible' }
    } else {
    return numValue < 50
        ? { color: COLORS.success, badgeClass: 'badge-success', badgeText: 'Faible' }
        : { color: COLORS.danger, badgeClass: 'badge-danger', badgeText: 'Élevé' }
    }
}, [numValue, isFavorable])

// Animation du gauge
useEffect(() => {
    if (!fillRef.current || !counterRef.current) return
    
    const target = numValue
    const duration = 800
    const start = performance.now()
    
    const easeOut = (t) => 1 - Math.pow(1 - t, 3)
    
    // Initialiser
    fillRef.current.style.setProperty('--g', '0deg')
    
    const animate = (now) => {
    const progress = Math.min(1, (now - start) / duration)
    const eased = easeOut(progress)
    
    // Animer le fill (180° = 100%)
    const angle = target * 1.8 * eased
    fillRef.current.style.setProperty('--g', `${angle.toFixed(1)}deg`)
    
    // Animer le compteur
    counterRef.current.textContent = Math.round(target * eased)
    
    if (progress < 1) {
        requestAnimationFrame(animate)
    } else {
        counterRef.current.textContent = Math.round(target)
    }
    }
    
    // Délai pour l'effet cascade
    setTimeout(() => requestAnimationFrame(animate), 100)
}, [numValue])

return (
    <div className={clsx('card text-center h-full relative overflow-hidden group', className)}>
    {/* Gauge semi-circulaire */}
    <div className="gauge-wrapper mb-3">
        <div className="gauge-bg" />
        <div 
        ref={fillRef}
        className="gauge-fill"
        style={{ '--gauge-color': color }}
        data-target={numValue}
        />
        <div className="gauge-inner" />
        <div className="gauge-tick" />
    </div>
    
    {/* Valeur */}
    <div className="text-2xl font-bold text-slate-800 font-mono mb-0.5">
        <span ref={counterRef} className="transition-colors" style={{ color }}>{numValue}</span>
        <span className="text-base font-medium text-muted">%</span>
    </div>
    
    {/* Label */}
    <p className="font-semibold text-slate-700 text-sm">{label}</p>
    
    {/* Sous-label */}
    {sublabel && (
        <p className="text-xs text-muted mt-0.5 leading-relaxed">{sublabel}</p>
    )}
    
    {/* Badge */}
    <span className={clsx('badge mt-2', badgeClass)}>
        {badgeText}
    </span>
    </div>
)
}