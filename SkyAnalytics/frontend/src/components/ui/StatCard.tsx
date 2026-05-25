'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

// ===================================================
// STAT CARD COMPONENT - Tarjeta de estadística KPI
// ===================================================

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ReactNode
  trend?: {
    value: number
    label: string
  }
  color?: 'sky' | 'emerald' | 'amber' | 'rose' | 'violet'
  onClick?: () => void
  loading?: boolean
}

const colorVariants = {
  sky: {
    bg: 'bg-sky-500/15',
    icon: 'text-sky-400',
    border: 'hover:border-sky-500/30',
  },
  emerald: {
    bg: 'bg-emerald-500/15',
    icon: 'text-emerald-400',
    border: 'hover:border-emerald-500/30',
  },
  amber: {
    bg: 'bg-amber-500/15',
    icon: 'text-amber-400',
    border: 'hover:border-amber-500/30',
  },
  rose: {
    bg: 'bg-rose-500/15',
    icon: 'text-rose-400',
    border: 'hover:border-rose-500/30',
  },
  violet: {
    bg: 'bg-violet-500/15',
    icon: 'text-violet-400',
    border: 'hover:border-violet-500/30',
  },
}

export function StatCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  color = 'sky',
  onClick,
  loading = false,
}: StatCardProps) {
  const colors = colorVariants[color]

  if (loading) {
    return (
      <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6 animate-pulse">
        <div className="flex items-start justify-between">
          <div className="space-y-3 flex-1">
            <div className="h-4 w-24 bg-white/10 rounded" />
            <div className="h-8 w-32 bg-white/10 rounded" />
            {subtitle && <div className="h-3 w-20 bg-white/10 rounded" />}
          </div>
          <div className={`p-3 rounded-xl ${colors.bg}`}>
            <div className="h-6 w-6 bg-white/10 rounded" />
          </div>
        </div>
      </div>
    )
  }

  const CardWrapper = onClick ? motion.button : 'div'
  const wrapperProps = onClick
    ? {
      whileHover: { y: -2 },
      whileTap: { scale: 0.98 },
      onClick,
      className: 'w-full text-left cursor-pointer transition-shadow hover:shadow-lg',
    }
    : { className: 'w-full' }

  return (
    <CardWrapper
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      {...wrapperProps}
    >
      <div
        className={cn(
          'backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6',
          'transition-all duration-200',
          onClick && `hover:bg-white/10 cursor-pointer ${colors.border}`
        )}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <p className="text-xs sm:text-sm font-medium text-slate-400 truncate">{title}</p>
            <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-white mt-1 truncate">{value}</p>

            {subtitle && (
              <p className="text-[10px] sm:text-xs text-slate-500 mt-1 truncate">{subtitle}</p>
            )}

            {trend && (
              <div className="flex items-center gap-1.5 mt-2">
                <span
                  className={cn(
                    'text-xs font-semibold',
                    trend.value >= 0 ? 'text-emerald-400' : 'text-rose-400'
                  )}
                >
                  {trend.value >= 0 ? '+' : ''}{trend.value}%
                </span>
                <span className="text-xs text-slate-500">{trend.label}</span>
              </div>
            )}
          </div>

          <div className={cn('p-3 rounded-xl flex-shrink-0', colors.bg)}>
            <div className={colors.icon}>{icon}</div>
          </div>
        </div>
      </div>
    </CardWrapper>
  )
}
