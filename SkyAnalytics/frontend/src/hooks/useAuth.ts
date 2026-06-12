import { useAuthStore } from '@/store/auth'
import type { UserRole } from '@/types/database'

export interface AuthUser {
  id: number
  email: string
  full_name: string | null
  role: UserRole
  is_active: boolean
}

export function useAuth() {
  const { user, token, isAuthenticated, login, logout, updateUser } = useAuthStore()

  return {
    user: user as AuthUser | null,
    token,
    isAuthenticated,
    login,
    logout,
    updateUser,
  }
}
