import { motion } from 'framer-motion'

interface LoadingSpinnerProps {
    size?: 'sm' | 'md' | 'lg'
    className?: string
}

export function LoadingSpinner({ size = 'md', className = '' }: LoadingSpinnerProps) {
    const sizeClasses = {
        sm: 'h-4 w-4',
        md: 'h-8 w-8',
        lg: 'h-12 w-12',
    }

    return (
        <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className={`border-2 border-white/20 border-t-white rounded-full ${sizeClasses[size]} ${className}`}
        />
    )
}

interface LoadingSkeletonProps {
    className?: string
}

export function LoadingSkeleton({ className = '' }: LoadingSkeletonProps) {
    return (
        <div className={`animate-pulse bg-white/10 rounded ${className}`} />
    )
}