'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Menu, X, BarChart3, Users, Map, Settings, LogOut } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuthStore } from '@/store/auth'

interface DashboardLayoutProps {
    children: React.ReactNode
}

const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
    { name: 'Usuarios', href: '/users', icon: Users },
    { name: 'Mapas', href: '/maps', icon: Map },
    { name: 'Configuración', href: '/settings', icon: Settings },
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const pathname = usePathname()
    const { user, logout } = useAuthStore()

    return (
        <div className="min-h-screen bg-gray-900">
            {/* Mobile sidebar backdrop */}
            {sidebarOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-40 bg-black/50 lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Sidebar */}
            <motion.div
                initial={false}
                animate={{ x: sidebarOpen ? 0 : -280 }}
                className="fixed left-0 top-0 z-50 h-full w-64 bg-gray-800 shadow-xl"
            >
                <div className="flex h-16 items-center justify-between px-4">
                    <h1 className="text-xl font-bold text-white">SkyAnalytics</h1>
                    <button
                        onClick={() => setSidebarOpen(false)}
                        className="text-gray-400 hover:text-white lg:hidden"
                    >
                        <X className="h-6 w-6" />
                    </button>
                </div>

                <nav className="mt-8 px-4">
                    <ul className="space-y-2">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href
                            return (
                                <li key={item.name}>
                                    <Link
                                        href={item.href}
                                        className={`flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors ${isActive
                                                ? 'bg-blue-600 text-white'
                                                : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                                            }`}
                                        onClick={() => setSidebarOpen(false)}
                                    >
                                        <item.icon className="mr-3 h-5 w-5" />
                                        {item.name}
                                    </Link>
                                </li>
                            )
                        })}
                    </ul>
                </nav>

                <div className="absolute bottom-4 left-4 right-4">
                    <div className="rounded-lg bg-gray-700 p-3">
                        <p className="text-sm text-gray-300">{user?.full_name || user?.email}</p>
                        <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
                    </div>
                    <button
                        onClick={logout}
                        className="mt-2 flex w-full items-center rounded-lg px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white"
                    >
                        <LogOut className="mr-3 h-5 w-5" />
                        Cerrar Sesión
                    </button>
                </div>
            </motion.div>

            {/* Main content */}
            <div className="lg:pl-64">
                {/* Top bar */}
                <div className="sticky top-0 z-30 flex h-16 items-center justify-between bg-gray-900 px-4 shadow-sm lg:px-6">
                    <button
                        onClick={() => setSidebarOpen(true)}
                        className="text-gray-400 hover:text-white lg:hidden"
                    >
                        <Menu className="h-6 w-6" />
                    </button>
                    <div className="flex-1" />
                    <div className="flex items-center space-x-4">
                        {/* Notifications, etc. */}
                    </div>
                </div>

                {/* Page content */}
                <main className="p-4 lg:p-6">
                    {children}
                </main>
            </div>
        </div>
    )
}