import { motion } from 'framer-motion'
import { ReactNode } from 'react'

interface ButtonProps {
    children: ReactNode
    variant?: 'primary' | 'secondary' | 'danger'
    size?: 'sm' | 'md' | 'lg'
    disabled?: boolean
    loading?: boolean
    onClick?: () => void
    type?: 'button' | 'submit' | 'reset'
    className?: string
}

export function Button({
    children,
    variant = 'primary',
    size = 'md',
    disabled = false,
    loading = false,
    onClick,
    type = 'button',
    className = '',
}: ButtonProps) {
    const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed'

    const variantClasses = {
        primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500',
        secondary: 'bg-white/10 hover:bg-white/20 text-white border border-white/20 focus:ring-white/50',
        danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500',
    }

    const sizeClasses = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
    }

    return (
        <motion.button
            whileHover={!disabled && !loading ? { scale: 1.02 } : {}}
            whileTap={!disabled && !loading ? { scale: 0.98 } : {}}
            type={type}
            disabled={disabled || loading}
            onClick={onClick}
            className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
        >
            {loading && (
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="mr-2 h-4 w-4 border-2 border-white/20 border-t-white rounded-full"
                />
            )}
            {children}
        </motion.button>
    )
}