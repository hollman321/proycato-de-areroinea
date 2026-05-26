import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
    id: number
    email: string
    full_name: string | null
    role: string
    is_active: boolean
}

interface AuthState {
    user: User | null
    token: string | null
    isAuthenticated: boolean
    login: (user: User, token: string) => void
    logout: () => void
    updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            login: (user: User, token: string) => {
                if (typeof window !== 'undefined') {
                    localStorage.setItem('auth-token', token)
                    document.cookie = `auth-token=${token}; path=/; max-age=${60 * 60 * 24 * 30}`
                }
                set({ user, token, isAuthenticated: true })
            },
            logout: () => {
                if (typeof window !== 'undefined') {
                    localStorage.removeItem('auth-token')
                    document.cookie = 'auth-token=; path=/; max-age=0'
                }
                set({ user: null, token: null, isAuthenticated: false })
            },
            updateUser: (updates: Partial<User>) => {
                const currentUser = get().user
                if (currentUser) {
                    set({ user: { ...currentUser, ...updates } })
                }
            },
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({ user: state.user, token: state.token, isAuthenticated: state.isAuthenticated }),
        }
    )
)