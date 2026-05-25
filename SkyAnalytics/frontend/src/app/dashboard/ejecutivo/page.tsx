'use client'

import { useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend, AreaChart, Area } from 'recharts'
import ClientOnly from '@/components/ClientOnly'
import { RefreshCcw, Download, Sparkles, CalendarDays, ChevronRight, TrendingUp } from 'lucide-react'
import { jsPDF } from 'jspdf'
import api, { getWithFallback } from '@/services/api'
import { mockDashboardResumen, mockTendenciasMensuales, mockPaises, mockAIRecommendations } from '@/services/mockData'
import { downloadExcel } from '@/utils/export'

function formatCurrency(value: number) {
    return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export default function EjecutivoPage() {
    const queryClient = useQueryClient()
    const [fechaDesde, setFechaDesde] = useState('')
    const [fechaHasta, setFechaHasta] = useState('')

    const { data: resumen } = useQuery({
        queryKey: ['ejecutivo-resumen'],
        queryFn: async () => {
            return await getWithFallback('/analytics/resumen', mockDashboardResumen)
        },
        staleTime: 60000,
    })

    const { data: tendencias } = useQuery({
        queryKey: ['ejecutivo-tendencias'],
        queryFn: async () => {
            return await getWithFallback('/analytics/tendencia-mensual', mockTendenciasMensuales)
        },
    })

    const { data: paises } = useQuery({
        queryKey: ['ejecutivo-paises', fechaDesde, fechaHasta],
        queryFn: async () => {
            const params: Record<string, string> = {}
            if (fechaDesde) params.fecha_inicio = fechaDesde
            if (fechaHasta) params.fecha_fin = fechaHasta
            return await getWithFallback('/analytics/por-pais', mockPaises, { params })
        },
    })

    const { data: aiRecommendations } = useQuery({
        queryKey: ['ejecutivo-ia'],
        queryFn: async () => {
            return await getWithFallback('/admin/enterprise/ai/recommendations', mockAIRecommendations)
        },
        staleTime: 120000,
    })

    const topPaises = useMemo(() => (paises || []).slice(0, 6), [paises])

    const handleRefresh = () => {
        queryClient.invalidateQueries({ queryKey: ['ejecutivo-resumen'] })
        queryClient.invalidateQueries({ queryKey: ['ejecutivo-tendencias'] })
        queryClient.invalidateQueries({ queryKey: ['ejecutivo-paises'] })
        queryClient.invalidateQueries({ queryKey: ['ejecutivo-ia'] })
    }

    const handleExportExcel = () => {
        const rows = [
            {
                KPI: 'Usuarios activos',
                Valor: resumen?.usuarios_activos || 0,
            },
            {
                KPI: 'Viajes completados',
                Valor: resumen?.viajes_completados || 0,
            },
            {
                KPI: 'Ingresos',
                Valor: resumen?.ingresos || 0,
            },
        ]
        downloadExcel(rows, 'reporte_ejecutivo')
    }

    const handleExportPdf = () => {
        const doc = new jsPDF({ orientation: 'landscape' })
        doc.setFontSize(16)
        doc.text('Reporte Ejecutivo - SkyAnalytics', 14, 20)
        doc.setFontSize(11)
        doc.text(`Usuarios activos: ${resumen?.usuarios_activos ?? 'N/A'}`, 14, 36)
        doc.text(`Viajes completados: ${resumen?.viajes_completados ?? 'N/A'}`, 14, 46)
        doc.text(`Ingresos totales: ${formatCurrency(resumen?.ingresos ?? 0)}`, 14, 56)
        doc.save('reporte_ejecutivo.pdf')
    }

    return (
        <div className="space-y-6 min-w-0">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">Ejecutivo</h1>
                    <p className="text-gray-400 mt-2">Métricas comparativas, alertas críticas y panel ejecutivo con filtros.</p>
                </div>
                <div className="flex flex-wrap gap-3">
                    <button
                        type="button"
                        onClick={handleRefresh}
                        className="inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500"
                    >
                        <RefreshCcw className="h-4 w-4" />
                        Actualizar métricas
                    </button>
                    <button
                        type="button"
                        onClick={handleExportExcel}
                        className="inline-flex items-center gap-2 rounded-2xl bg-slate-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-600"
                    >
                        <Download className="h-4 w-4" />
                        Exportar Excel
                    </button>
                    <button
                        type="button"
                        onClick={handleExportPdf}
                        className="inline-flex items-center gap-2 rounded-2xl bg-slate-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-600"
                    >
                        <Download className="h-4 w-4" />
                        Exportar PDF
                    </button>
                </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
                <div className="grid gap-6 lg:grid-cols-2">
                    <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                        <p className="text-sm uppercase tracking-[0.2em] text-sky-400">KPI Ejecutivo</p>
                        <div className="mt-6 grid gap-4 sm:grid-cols-2">
                            {[
                                { label: 'Usuarios activos', value: resumen?.usuarios_activos || 0 },
                                { label: 'Viajes completados', value: resumen?.viajes_completados || 0 },
                                { label: 'Ingresos', value: formatCurrency(resumen?.ingresos || 0) },
                                { label: 'Clientes frecuentes', value: resumen?.clientes_frecuentes || 0 },
                            ].map((item) => (
                                <div key={item.label} className="rounded-3xl bg-white/5 p-4">
                                    <p className="text-sm text-gray-400">{item.label}</p>
                                    <p className="mt-2 text-2xl font-semibold text-white">{item.value}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                        <div className="flex items-center justify-between">
                            <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Resumen IA</p>
                            <Sparkles className="h-5 w-5 text-sky-400" />
                        </div>
                        <div className="mt-6 space-y-4">
                            {(aiRecommendations?.recommendations ?? []).slice(0, 3).map((item: any) => (
                                <div key={item.id} className="rounded-3xl bg-slate-900/80 p-4">
                                    <div className="flex items-start justify-between gap-4">
                                        <div>
                                            <p className="font-semibold text-white">{item.title}</p>
                                            <p className="text-sm text-gray-400 mt-1">{item.description}</p>
                                        </div>
                                        <span className="rounded-full bg-sky-500/15 px-3 py-1 text-xs font-semibold text-sky-200">{item.confidence}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                    <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Filtros por periodo</p>
                    <div className="mt-4 grid gap-4 sm:grid-cols-2">
                        <label className="space-y-2 text-sm text-gray-300">
                            Fecha desde
                            <input
                                type="date"
                                value={fechaDesde}
                                onChange={(event) => setFechaDesde(event.target.value)}
                                className="w-full rounded-2xl border border-white/10 bg-slate-950/90 px-4 py-3 text-white outline-none focus:border-sky-500"
                            />
                        </label>
                        <label className="space-y-2 text-sm text-gray-300">
                            Fecha hasta
                            <input
                                type="date"
                                value={fechaHasta}
                                onChange={(event) => setFechaHasta(event.target.value)}
                                className="w-full rounded-2xl border border-white/10 bg-slate-950/90 px-4 py-3 text-white outline-none focus:border-sky-500"
                            />
                        </label>
                    </div>
                    <p className="mt-6 text-sm text-gray-400">El panel se actualiza con filtros para comparar tendencias de países y demanda.</p>
                </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
                <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                    <div className="flex items-center justify-between">
                        <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Tendencia mensual</p>
                        <span className="text-sm text-gray-400">Últimos 12 meses</span>
                    </div>
                    <div className="mt-6 h-72">
                        <ClientOnly>
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={tendencias || []} margin={{ left: -12, right: 0, top: 6, bottom: 6 }}>
                                    <CartesianGrid strokeDasharray="4 4" stroke="#334155" />
                                    <XAxis dataKey="mes" stroke="#94A3B8" />
                                    <YAxis stroke="#94A3B8" />
                                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderRadius: '10px', border: '1px solid #334155' }} />
                                    <Line type="monotone" dataKey="valor" stroke="#38bdf8" strokeWidth={3} dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </ClientOnly>
                    </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                    <div className="flex items-center justify-between">
                        <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Países clave</p>
                        <p className="text-sm text-gray-400">Top 6</p>
                    </div>
                    <div className="mt-6 space-y-3">
                        {topPaises.map((item: any) => (
                            <div key={item.name} className="rounded-3xl bg-slate-900/80 p-4">
                                <div className="flex items-center justify-between gap-3">
                                    <div>
                                        <p className="text-sm font-semibold text-white">{item.name}</p>
                                        <p className="text-xs text-gray-400">{item.value} viajes</p>
                                    </div>
                                    <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-gray-200">{item.porcentaje ? `${item.porcentaje}%` : ''}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                <div className="flex items-center justify-between">
                    <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Metas operativas</p>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                        <CalendarDays className="h-4 w-4" />
                        Actualizado hace poco
                    </div>
                </div>
                <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    {[
                        { label: 'Crecimiento vs mes pasado', value: '14%', accent: 'bg-emerald-500/10 text-emerald-300' },
                        { label: 'Alertas críticas abiertas', value: '3', accent: 'bg-rose-500/10 text-rose-300' },
                        { label: 'Score de satisfacción', value: '88.4', accent: 'bg-sky-500/10 text-sky-300' },
                        { label: 'NPS estimado', value: '76', accent: 'bg-violet-500/10 text-violet-300' },
                    ].map((item) => (
                        <div key={item.label} className={`rounded-3xl border border-white/10 p-4 ${item.accent}`}>
                            <p className="text-sm text-gray-300">{item.label}</p>
                            <p className="mt-3 text-2xl font-semibold text-white">{item.value}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
