'use client'

import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Users, Plane, DollarSign, TrendingUp, MapPin, Clock } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'
import { DashboardLayout } from '@/layouts/DashboardLayout'
import api from '@/services/api'
import { DashboardStats, ChartData } from '@/types'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

function StatCard({ title, value, icon: Icon, color, delay }: {
    title: string
    value: string | number
    icon: any
    color: string
    delay: number
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay }}
            className="backdrop-blur-xl bg-white/10 rounded-xl border border-white/20 p-6 shadow-lg"
        >
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-gray-400 text-sm font-medium">{title}</p>
                    <p className="text-2xl font-bold text-white mt-1">{value}</p>
                </div>
                <div className={`p-3 rounded-lg ${color}`}>
                    <Icon className="h-6 w-6 text-white" />
                </div>
            </div>
        </motion.div>
    )
}

export default function DashboardPage() {
    const { data: stats, isLoading } = useQuery({
        queryKey: ['dashboard-stats'],
        queryFn: async () => {
            const response = await api.get('/analytics/resumen')
            return response.data as DashboardStats
        },
        refetchInterval: 30000, // Refresh every 30 seconds
    })

    const { data: chartData } = useQuery({
        queryKey: ['chart-data'],
        queryFn: async () => {
            const response = await api.get('/analytics/viajes-por-pais')
            return response.data as ChartData[]
        },
    })

    if (isLoading) {
        return (
            <DashboardLayout>
                <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[...Array(6)].map((_, i) => (
                            <div key={i} className="backdrop-blur-xl bg-white/10 rounded-xl border border-white/20 p-6 animate-pulse">
                                <div className="h-4 bg-white/20 rounded mb-2"></div>
                                <div className="h-8 bg-white/20 rounded"></div>
                            </div>
                        ))}
                    </div>
                </div>
            </DashboardLayout>
        )
    }

    return (
        <DashboardLayout>
            <div className="space-y-6">
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold text-white">Dashboard</h1>
                    <p className="text-gray-400 mt-2">Resumen operacional de SkyAnalytics</p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <StatCard
                        title="Usuarios Activos"
                        value={stats?.usuarios_activos || 0}
                        icon={Users}
                        color="bg-blue-500"
                        delay={0}
                    />
                    <StatCard
                        title="Viajes Completados"
                        value={stats?.viajes_completados || 0}
                        icon={Plane}
                        color="bg-green-500"
                        delay={0.1}
                    />
                    <StatCard
                        title="Ingresos Totales"
                        value={`$${stats?.ingresos?.toLocaleString() || 0}`}
                        icon={DollarSign}
                        color="bg-yellow-500"
                        delay={0.2}
                    />
                    <StatCard
                        title="Clientes Frecuentes"
                        value={stats?.clientes_frecuentes || 0}
                        icon={TrendingUp}
                        color="bg-purple-500"
                        delay={0.3}
                    />
                    <StatCard
                        title="País Más Activo"
                        value={stats?.pais_mas_activo || 'N/A'}
                        icon={MapPin}
                        color="bg-red-500"
                        delay={0.4}
                    />
                    <StatCard
                        title="Tiempo Promedio"
                        value={`${stats?.tiempo_promedio || 0} min`}
                        icon={Clock}
                        color="bg-indigo-500"
                        delay={0.5}
                    />
                </div>

                {/* Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Bar Chart */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 }}
                        className="backdrop-blur-xl bg-white/10 rounded-xl border border-white/20 p-6"
                    >
                        <h3 className="text-xl font-semibold text-white mb-4">Viajes por País</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="name" stroke="#9CA3AF" />
                                <YAxis stroke="#9CA3AF" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1F2937',
                                        border: '1px solid #374151',
                                        borderRadius: '8px',
                                    }}
                                />
                                <Bar dataKey="value" fill="#3B82F6" />
                            </BarChart>
                        </ResponsiveContainer>
                    </motion.div>

                    {/* Pie Chart */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.7 }}
                        className="backdrop-blur-xl bg-white/10 rounded-xl border border-white/20 p-6"
                    >
                        <h3 className="text-xl font-semibold text-white mb-4">Distribución por Categoría</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={chartData?.slice(0, 5)}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {chartData?.slice(0, 5).map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </motion.div>
                </div>

                {/* Popular Routes */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8 }}
                    className="backdrop-blur-xl bg-white/10 rounded-xl border border-white/20 p-6"
                >
                    <h3 className="text-xl font-semibold text-white mb-4">Rutas Más Populares</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {stats?.rutas_populares?.map((route, index) => (
                            <div key={index} className="bg-white/5 rounded-lg p-4">
                                <p className="text-white font-medium">{route}</p>
                                <p className="text-gray-400 text-sm">Ruta #{index + 1}</p>
                            </div>
                        ))}
                    </div>
                </motion.div>
            </div>
        </DashboardLayout>
    )
}