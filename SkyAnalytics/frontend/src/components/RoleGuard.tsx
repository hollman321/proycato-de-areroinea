'use client'

import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

interface RoleGuardProps {
  children: React.ReactNode
  allowedRoles: string[]
  fallback?: React.ReactNode
}

export const RoleGuard = ({ children, allowedRoles, fallback = null }: RoleGuardProps) => {
  const { user, isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }

    if (user && !allowedRoles.includes(user.role)) {
      router.push('/unauthorized')
    }
  }, [isAuthenticated, user, allowedRoles, router])

  if (!isAuthenticated) {
    return <>{fallback}</>
  }

  if (!user || !allowedRoles.includes(user.role)) {
    return <>{fallback}</>
  }

  return <>{children}</>
}
