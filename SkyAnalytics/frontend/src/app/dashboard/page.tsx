'use client'

import { useMemo } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
    BarChart3,
    Users,
    Plane,
    DollarSign,
    TrendingUp,
    Activity,
    RefreshCw,
    Clock,
    ShieldCheck
} from 'lucide-react'
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    Cell
} from 'recharts'
import { StatCard } from '@/components/ui/StatCard'
import { Button } from '@/components/ui/Card'
import ClientOnly from '@/components/ClientOnly'
import { useToast } from '@/providers/ToastProvider'
import { motion } from 'framer-motion'
import axios from 'axios'

const CHART_COLORS = {
    ops: ['#38bdf8', '#fbbf24', '#10b981', '#f87171']
}

export default function DashboardPage() {
    const queryClient = useQueryClient()
    const { success, info } = useToast()

    // Data Fetching real de los módulos construidos
    const { data: financeData, isLoading: loadingFinance } = useQuery({
        queryKey: ['finance-summary'],
        queryFn: async () => (await axios.get('/api/finance')).data
    })

    const { data: opsData, isLoading: loadingOps } = useQuery({
        queryKey: ['ops-summary'],
        queryFn: async () => (await axios.get('/api/operations')).data
    })

    const { data: clientsData, isLoading: loadingClients } = useQuery({
        queryKey: ['clients-summary'],
        queryFn: async () => (await axios.get('/api/clients')).data
    })

    const handleRefresh = () => {
        queryClient.invalidateQueries()
        success('Métricas actualizadas en tiempo real')
    }

    // Agregación de estadísticas para KPIs
    const stats = useMemo(() => {
        const totalBalance = (financeData || []).reduce((acc: number, t: any) =>
            t.type === 'INCOME' ? acc + t.amount : acc - t.amount, 0)

        const activeOps = (opsData || []).filter((o: any) => o.status === 'IN_PROGRESS').length
        const totalClients = (clientsData || []).length

        return {
            balance: totalBalance,
            activeOps,
            totalClients
        }
    }, [financeData, opsData, clientsData])

    // Datos para el gráfico de tendencia financiera
    const financeChartData = useMemo(() => {
        if (!financeData) return []
        return financeData.slice(0, 7).reverse().map((t: any) => ({
            name: new Date(t.date).toLocaleDateString('es-ES', { day: '2-digit', month: 'short' }),
            amount: t.amount
        }))
    }, [financeData])

    // Datos para el gráfico de distribución de operaciones
    const opsChartData = useMemo(() => {
        if (!opsData) return []
        const counts = (opsData as any[]).reduce((acc: any, op: any) => {
            acc[op.status] = (acc[op.status] || 0) + 1
            return acc
        }, {})

        return [
            { name: 'Pendientes', value: counts['PENDING'] || 0 },
            { name: 'En Proceso', value: counts['IN_PROGRESS'] || 0 },
            { name: 'Completados', value: counts['COMPLETED'] || 0 },
            { name: 'Cancelados', value: counts['CANCELLED'] || 0 },
        ]
    }, [opsData])

    const formatCurrency = (val: number) =>
        new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)

    return (
        <div className="space-y-8">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white">Resumen Ejecutivo</h1>
                    <p className="text-slate-400 mt-1">Operational Intelligence Center en tiempo real.</p>
                </div>
                <div className="flex items-center gap-3">
                    <Button
                        variant="secondary"
                        size="sm"
                        icon={<RefreshCw className={`h-4 w-4 ${loadingFinance ? 'animate-spin' : ''}`} />}
                        onClick={handleRefresh}
                    >
                        Actualizar Datos
                    </Button>
                </div>
            </div>

            {/* Fila de KPIs - Grid Adaptativo Real */}
            <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
                <StatCard title="Revenue Total" value={formatCurrency(stats.balance)} trend={{ value: 8.2, label: 'mensual' }} icon={<DollarSign className="h-5 w-5 sm:h-6 sm:w-6" />} color="emerald" loading={loadingFinance} />
                <StatCard title="Operaciones Activas" value={stats.activeOps} trend={{ value: 12.5, label: 'incremento' }} icon={<Plane className="h-5 w-5 sm:h-6 sm:w-6" />} color="sky" loading={loadingOps} />
                <StatCard title="Total Clientes" value={stats.totalClients} icon={<Users className="h-5 w-5 sm:h-6 sm:w-6" />} color="violet" loading={loadingClients} />
                <StatCard title="Eficiencia" value="94.2%" trend={{ value: 2.1, label: 'mejoría' }} icon={<Activity className="h-5 w-5 sm:h-6 sm:w-6" />} color="amber" loading={loadingOps} />
            </div>

            {/* Fila de Gráficos - Expansión Máxima */}
            <div className="grid gap-6 xl:gap-8 grid-cols-1 xl:grid-cols-2">
                <div className="rounded-3xl border border-white/5 bg-slate-900/50 p-6 sm:p-8 backdrop-blur-xl shadow-2xl flex flex-col">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h3 className="text-lg font-bold text-white">Tendencia de Flujo</h3>
                            <p className="text-sm text-slate-400">Últimos movimientos financieros</p>
                        </div>
                        <TrendingUp className="h-5 w-5 text-emerald-400" />
                    </div>
                    <div className="h-[350px] sm:h-[400px] w-full flex-1">
                        <ClientOnly>
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={financeChartData}>
                                    <defs>
                                        <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                                    <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `$${val}`} />
                                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: '1px solid #ffffff10' }} />
                                    <Area type="monotone" dataKey="amount" stroke="#0ea5e9" strokeWidth={3} fillOpacity={1} fill="url(#colorAmount)" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </ClientOnly>
                    </div>
                </div>

                <div className="rounded-3xl border border-white/5 bg-slate-900/50 p-6 sm:p-8 backdrop-blur-xl shadow-2xl flex flex-col">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h3 className="text-lg font-bold text-white">Estado de Operaciones</h3>
                            <p className="text-sm text-slate-400">Carga de trabajo por estatus</p>
                        </div>
                        <BarChart3 className="h-5 w-5 text-sky-400" />
                    </div>
                    <div className="h-[350px] sm:h-[400px] w-full flex-1">
                        <ClientOnly>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={opsChartData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                                    <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                                    <Tooltip cursor={{ fill: '#ffffff05' }} contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: '1px solid #ffffff10' }} />
                                    <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                                        {opsChartData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={CHART_COLORS.ops[index % CHART_COLORS.ops.length]} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </ClientOnly>
                    </div>
                </div>
            </div>

            {/* Actividad Reciente y Estado de Servicios */}
            <div className="grid gap-6 lg:grid-cols-3">
                <div className="lg:col-span-2 rounded-3xl border border-white/5 bg-slate-900/50 p-6 backdrop-blur-xl shadow-2xl">
                    <div className="flex items-center gap-2 mb-6">
                        <Clock className="h-5 w-5 text-sky-400" />
                        <h3 className="text-lg font-bold text-white">Actividad Reciente</h3>
                    </div>
                    <div className="space-y-4">
                        {[
                            { id: 1, type: 'op', title: 'Operación SKY-201 completada', time: 'hace 5 min', color: 'text-emerald-400' },
                            { id: 2, type: 'fin', title: 'Nuevo ingreso registrado: $4,200', time: 'hace 12 min', color: 'text-sky-400' },
                            { id: 3, type: 'user', title: 'Acceso detectado desde Ciudad de México', time: 'hace 45 min', color: 'text-amber-400' }
                        ].map((item) => (
                            <div key={item.id} className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5 group hover:bg-white/10 transition-colors">
                                <div className="flex items-center gap-4">
                                    <div className={`h-2 w-2 rounded-full ${item.color.replace('text', 'bg')}`} />
                                    <p className="text-sm font-medium text-slate-200">{item.title}</p>
                                </div>
                                <span className="text-xs text-slate-500">{item.time}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="rounded-3xl border border-white/5 bg-slate-900/50 p-6 backdrop-blur-xl shadow-2xl">
                    <div className="flex items-center gap-2 mb-6">
                        <ShieldCheck className="h-5 w-5 text-emerald-400" />
                        <h3 className="text-lg font-bold text-white">Estado del Sistema</h3>
                    </div>
                    <div className="space-y-6">
                        {[
                            { name: 'API Gateway', status: 'Online', latency: '24ms' },
                            { name: 'PostgreSQL DB', status: 'Online', latency: '12ms' },
                            { name: 'IA Engine', status: 'Processing', latency: '450ms' }
                        ].map((service) => (
                            <div key={service.name} className="flex flex-col gap-2">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm font-medium text-slate-300">{service.name}</span>
                                    <span className="text-xs font-bold text-emerald-400">{service.status}</span>
                                </div>
                                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: '100%' }}
                                        className="h-full bg-emerald-500/50"
                                    />
                                </div>
                                <span className="text-[10px] text-slate-500">Latencia: {service.latency}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}