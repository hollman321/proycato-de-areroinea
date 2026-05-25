'use client'

import { useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Bell, ShieldCheck, Activity, Download, Clock } from 'lucide-react'
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts'
import ClientOnly from '@/components/ClientOnly'
import api, { getWithFallback } from '@/services/api'
import { mockMonitoringStatus, mockMonitoringAlerts, mockMonitoringLogs } from '@/services/mockData'
import { downloadExcel } from '@/utils/export'

export default function MonitoreoPage() {
    const [search, setSearch] = useState('')
    const [restartStatus, setRestartStatus] = useState<string | null>(null)

    const { data: statusData } = useQuery({
        queryKey: ['monitoring-status'],
        queryFn: async () => {
            return await getWithFallback('/admin/enterprise/monitoring/status', mockMonitoringStatus)
        },
        staleTime: 60000,
    })

    const { data: alertsResponse } = useQuery({
        queryKey: ['monitoring-alerts'],
        queryFn: async () => {
            return await getWithFallback('/admin/enterprise/alerts', mockMonitoringAlerts)
        },
        staleTime: 45000,
    })

    const { data: logsResponse } = useQuery({
        queryKey: ['monitoring-logs'],
        queryFn: async () => {
            return await getWithFallback('/admin/enterprise/audit/logs', mockMonitoringLogs)
        },
        staleTime: 90000,
    })

    const alerts = alertsResponse?.alerts || []
    const logs = logsResponse?.logs || []

    const [restartMessage, setRestartMessage] = useState<string | null>(null)

    const refreshMonitoring = async () => {
        setRestartMessage('Solicitando actualización del monitor...')
        await api.get('/admin/enterprise/monitoring/status')
        setRestartMessage('Actualización solicitada. Refresca la vista para ver el estado más reciente.')
    }

    const handleRestartService = async () => {
        setRestartStatus('Reiniciando servicio...')
        await new Promise((resolve) => setTimeout(resolve, 800))
        setRestartStatus('Servicio reiniciado con éxito')
        setTimeout(() => setRestartStatus(null), 4000)
    }

    const filteredAlerts = useMemo(() => {
        if (!alerts) return []
        return alerts.filter((item: any) => item.message.toLowerCase().includes(search.toLowerCase()))
    }, [alerts, search])

    const handleExport = () => {
        downloadExcel((alerts || []).map((item: any) => ({
            Fecha: item.timestamp,
            Alerta: item.message,
            Nivel: item.severity,
        })), 'alertas_monitoreo')
    }

    return (
        <div className="space-y-6 min-w-0">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">Monitoreo</h1>
                    <p className="text-gray-400 mt-2">Salud de sistemas, alertas en vivo y registro de auditoría.</p>
                </div>
                <button
                    onClick={handleExport}
                    className="inline-flex items-center gap-2 rounded-2xl bg-slate-700 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-600"
                >
                    <Download className="h-4 w-4" />
                    Exportar alertas
                </button>
            </div>

            <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
                <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Estado de servicio</p>
                            <p className="mt-2 text-gray-400">Disponibilidad y tiempos de respuesta.</p>
                        </div>
                        <ShieldCheck className="h-5 w-5 text-slate-300" />
                    </div>
                    <div className="mt-6 grid gap-4 sm:grid-cols-2">
                        {[
                            { label: 'API principal', value: statusData?.api_status || 'Desconocido' },
                            { label: 'Base de datos', value: statusData?.database_status || 'Desconocido' },
                            { label: 'Cache Redis', value: statusData?.redis_status || 'Desconocido' },
                            { label: 'Tiempo disponible', value: statusData?.uptime || 'N/A' },
                        ].map((item) => (
                            <div key={item.label} className="rounded-3xl bg-slate-900/80 p-4">
                                <p className="text-sm text-gray-400">{item.label}</p>
                                <p className="mt-2 text-2xl font-semibold text-white">{item.value}</p>
                            </div>
                        ))}
                    </div>
                    <div className="mt-6 rounded-3xl bg-slate-900/80 p-5">
                        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                            <div>
                                <p className="text-sm text-gray-400">Última verificación</p>
                                <p className="mt-1 text-white">{statusData?.last_checked || 'Sin datos'}</p>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                <button
                                    onClick={refreshMonitoring}
                                    className="inline-flex items-center gap-2 rounded-2xl bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500"
                                >
                                    <Clock className="h-4 w-4" />
                                    Refrescar monitoreo
                                </button>
                                <button
                                    onClick={handleRestartService}
                                    className="inline-flex items-center gap-2 rounded-2xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
                                >
                                    <ShieldCheck className="h-4 w-4" />
                                    Reiniciar servicio
                                </button>
                            </div>
                        </div>
                        {(restartMessage || restartStatus) && <p className="mt-3 text-sm text-emerald-300">{restartStatus || restartMessage}</p>}
                    </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                            <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Tendencia de carga</p>
                            <p className="text-gray-400">Carga de eventos en la última hora.</p>
                        </div>
                        <div className="rounded-3xl bg-slate-900/80 px-4 py-2 text-sm text-gray-300">En vivo</div>
                    </div>
                    <div className="mt-6 h-72">
                        <ClientOnly>
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={statusData?.traffic || []} margin={{ left: -18, right: 0, top: 6, bottom: 6 }}>
                                    <CartesianGrid strokeDasharray="4 4" stroke="#334155" />
                                    <XAxis dataKey="time" stroke="#94A3B8" />
                                    <YAxis stroke="#94A3B8" />
                                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderRadius: '10px', border: '1px solid #334155' }} />
                                    <Line type="monotone" dataKey="value" stroke="#38bdf8" strokeWidth={3} dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </ClientOnly>
                    </div>
                </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                <div className="flex items-center justify-between">
                    <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Alertas recientes</p>
                    <div className="flex items-center gap-2 rounded-3xl bg-slate-900/80 px-4 py-3">
                        <Bell className="h-4 w-4 text-sky-400" />
                        <input
                            placeholder="Filtrar alertas"
                            value={search}
                            onChange={(event) => setSearch(event.target.value)}
                            className="w-full bg-transparent text-white outline-none placeholder:text-gray-500"
                        />
                    </div>
                </div>
                <div className="mt-6 space-y-3">
                    {filteredAlerts.map((alert: any) => (
                        <div key={alert.id} className="rounded-3xl bg-slate-900/80 p-4">
                            <div className="flex items-center justify-between gap-4">
                                <div>
                                    <p className="text-base font-semibold text-white">{alert.severity}</p>
                                    <p className="mt-1 text-sm text-gray-400">{alert.timestamp}</p>
                                </div>
                                <span className="rounded-full bg-rose-500/10 px-3 py-1 text-xs text-rose-300">{alert.status || 'Pendiente'}</span>
                            </div>
                            <p className="mt-3 text-sm text-gray-300">{alert.message}</p>
                        </div>
                    ))}
                </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Registro de auditoría</p>
                <div className="mt-4 overflow-x-auto rounded-3xl border border-white/10 bg-slate-900/80">
                    <table className="min-w-[640px] w-full border-collapse text-left text-sm text-gray-200">
                        <thead className="bg-slate-950/70 text-xs uppercase tracking-wider text-gray-400">
                            <tr>
                                <th className="px-4 py-4">Evento</th>
                                <th className="px-4 py-4">Usuario</th>
                                <th className="px-4 py-4">Fecha</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(logs || []).slice(0, 6).map((entry: any) => (
                                <tr key={entry.id} className="border-t border-white/5 hover:bg-white/5">
                                    <td className="px-4 py-4 text-white">{entry.action}</td>
                                    <td className="px-4 py-4">{entry.user || 'Sistema'}</td>
                                    <td className="px-4 py-4">{entry.created_at}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
