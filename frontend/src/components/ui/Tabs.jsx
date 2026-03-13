import { clsx } from 'clsx'
import { createContext, useContext, useState } from 'react'

// Context pour gérer l'état des tabs
const TabsContext = createContext(null)

export function Tabs({ value, onValueChange, children, className }) {
return (
    <TabsContext.Provider value={{ value, onValueChange }}>
    <div className={className}>{children}</div>
    </TabsContext.Provider>
)
}

export function TabsList({ children, className }) {
return (
    <div className={clsx(
    'inline-flex bg-white border border-border rounded-xl p-1 gap-1 shadow-soft',
    className
    )}>
    {children}
    </div>
)
}

export function TabsTrigger({ value, children, className, ...props }) {
const { value: selectedValue, onValueChange } = useContext(TabsContext)
const isSelected = value === selectedValue

return (
    <button
    onClick={() => onValueChange?.(value)}
    className={clsx(
        'px-5 py-2 rounded-lg font-semibold text-sm transition-all duration-200',
        isSelected 
        ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-md' 
        : 'text-muted hover:text-slate-700 hover:bg-slate-50',
        className
    )}
    {...props}
    >
    {children}
    </button>
)
}

export function TabsContent({ value, children, className, ...props }) {
const { value: selectedValue } = useContext(TabsContext)

if (value !== selectedValue) return null

return (
    <div className={clsx('animate-fade-in', className)} {...props}>
    {children}
    </div>
)
}

export default { Tabs, TabsList, TabsTrigger, TabsContent }