'use client'

import { useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Activity, Cpu, Sparkles, Zap, Download } from 'lucide-react'
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts'
import ClientOnly from '@/components/ClientOnly'
import api, { getWithFallback } from '@/services/api'
import { mockAIRecommendations } from '@/services/mockData'
import { downloadExcel } from '@/utils/export'
import { useToast } from '@/providers/ToastProvider'

const COLORS = ['#38bdf8', '#7c3aed', '#22c55e', '#f97316', '#eab308']

export default function InteligenciaIA() {
    const [selectedId, setSelectedId] = useState<string | null>(null)
    const { success, error, info } = useToast()

    const { data: aiData } = useQuery({
        queryKey: ['ia-recommendations'],
        queryFn: async () => {
            return await getWithFallback('/admin/enterprise/ai/recommendations', mockAIRecommendations)
        },
        staleTime: 90000,
    })

    const applyMutation = useMutation({
        mutationFn: async (id: string) => {
            const response = await api.post('/admin/enterprise/ai/apply', { recommendation_id: id })
            return response.data
        },
        onSuccess: () => {
            success('Recomendación aplicada exitosamente.')
        },
        onError: () => {
            error('Error al aplicar la recomendación. Verifique los logs del sistema.')
        }
    })

    const summaryData = useMemo(() => {
        return (aiData?.recommendations || []).map((item: any) => ({ name: item.title, value: item.score || 0 }))
    }, [aiData])

    const handleExport = () => {
        downloadExcel((aiData?.recommendations || []).map((item: any) => ({
            Recomendacion: item.title,
            Prioridad: item.priority,
            Impacto: item.impact,
        })), 'ia_recomendaciones')
    }

    return (
        <div className="space-y-6 w-full flex flex-col">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">Inteligencia Artificial</h1>
                    <p className="text-gray-400 mt-2">Recomendaciones inteligentes, automatización de riesgo y simulaciones de decisiones.</p>
                </div>
                <button
                    onClick={handleExport}
                    className="inline-flex items-center gap-2 rounded-2xl bg-slate-700 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-600"
                >
                    <Download className="h-4 w-4" />
                    Exportar recomendaciones
                </button>
            </div>

            <div className="grid gap-6 xl:grid-cols-[400px_1fr]">
                <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                    <div className="flex items-center justify-between">
                        <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Resumen de IA</p>
                        <Cpu className="h-5 w-5 text-slate-300" />
                    </div>
                    <div className="mt-6 space-y-4">
                        <div className="rounded-3xl bg-slate-900/80 p-4">
                            <p className="text-sm text-gray-400">Modelos activos</p>
                            <p className="mt-2 text-2xl font-semibold text-white">{aiData?.active_models || 0}</p>
                        </div>
                        <div className="rounded-3xl bg-slate-900/80 p-4">
                            <p className="text-sm text-gray-400">Recomendaciones generadas</p>
                            <p className="mt-2 text-2xl font-semibold text-white">{aiData?.recommendations?.length || 0}</p>
                        </div>
                        <div className="rounded-3xl bg-slate-900/80 p-4">
                            <p className="text-sm text-gray-400">Precisión estimada</p>
                            <p className="mt-2 text-2xl font-semibold text-white">{aiData?.accuracy || 'N/A'}</p>
                        </div>
                    </div>
                </div>
                <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                    <div className="flex items-center justify-between">
                        <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Distribución de prioridad</p>
                        <Sparkles className="h-5 w-5 text-slate-300" />
                    </div>
                    <div className="mt-6 h-72">
                        <ClientOnly>
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie data={summaryData} dataKey="value" nameKey="name" innerRadius={56} outerRadius={110} paddingAngle={4}>
                                        {summaryData.map((entry: any, index: number) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderRadius: '10px', border: '1px solid #334155' }} />
                                    <Legend verticalAlign="bottom" iconType="circle" formatter={(value) => <span className="text-sm text-white">{value}</span>} />
                                </PieChart>
                            </ResponsiveContainer>
                        </ClientOnly>
                    </div>
                </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                <div className="flex items-center justify-between">
                    <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Recomendaciones</p>
                    <span className="text-xs uppercase tracking-[0.2em] text-gray-400">Acción inmediata</span>
                </div>
                <div className="mt-6 grid gap-4">
                    {(aiData?.recommendations || []).map((item: any) => (
                        <div key={item.id} className="rounded-3xl bg-slate-900/80 p-5 shadow-inner">
                            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                                <div>
                                    <p className="text-base font-semibold text-white">{item.title}</p>
                                    <p className="mt-2 text-sm text-gray-400">{item.description}</p>
                                </div>
                                <div className="flex flex-wrap items-center gap-2">
                                    <span className="rounded-full bg-sky-500/15 px-3 py-1 text-xs font-semibold text-sky-200">{item.priority}</span>
                                    <button
                                        onClick={() => {
                                            setSelectedId(item.id)
                                            applyMutation.mutate(item.id)
                                        }}
                                        className="rounded-2xl bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500"
                                    >
                                        <Zap className="h-4 w-4" />
                                        Aplicar
                                    </button>
                                </div>
                            </div>
                            {selectedId === item.id && applyMutation.isPending && (
                                <p className="mt-3 text-sm text-gray-300">Aplicando recomendación...</p>
                            )}
                            {selectedId === item.id && applyMutation.isSuccess && (
                                <p className="mt-3 text-sm text-emerald-300">Recomendación aplicada correctamente.</p>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div >
    )
}
