import { Loader2 } from 'lucide-react'
import { clsx } from 'clsx'

export default function LoadingSpinner({ 
size = 'md', 
text = 'Chargement...', 
className 
}) {
const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
}

return (
    <div className={clsx('flex flex-col items-center gap-3', className)}>
    <Loader2 className={clsx('animate-spin text-primary-500', sizeClasses[size])} />
    {text && (
        <span className="text-sm text-muted font-medium animate-pulse">
        {text}
        </span>
    )}
    </div>
)
}