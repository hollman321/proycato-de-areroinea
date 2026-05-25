'use client'

import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Play, Plus, Sparkles, Settings2, Download } from 'lucide-react'
import api, { getWithFallback } from '@/services/api'
import { mockWorkflows } from '@/services/mockData'
import { downloadExcel } from '@/utils/export'

export default function AutomatizacionPage() {
    const queryClient = useQueryClient()
    const [newWorkflowName, setNewWorkflowName] = useState('')
    const [activeWorkflow, setActiveWorkflow] = useState<any | null>(null)

    const { data } = useQuery({
        queryKey: ['workflows'],
        queryFn: async () => {
            return await getWithFallback('/admin/enterprise/workflows', mockWorkflows)
        },
        staleTime: 90000,
    })

    const workflows = data?.workflows || []

    const executeMutation = useMutation({
        mutationFn: async (id: string) => {
            const response = await api.post(`/admin/enterprise/workflows/execute`, { workflow_id: id })
            return response.data
        },
    })

    const [localWorkflows, setLocalWorkflows] = useState<any[]>([])

    const createWorkflow = () => {
        if (!newWorkflowName.trim()) return
        setLocalWorkflows((current) => [
            {
                id: `local-${Date.now()}`,
                name: newWorkflowName,
                state: 'idle',
                last_run: 'Nunca ejecutado',
            },
            ...current,
        ])
        setNewWorkflowName('')
    }

    const handleExport = () => {
        const exportData = [...localWorkflows, ...workflows].map((workflow: any) => ({
            Workflow: workflow.name,
            Estado: workflow.state,
            UltimaEjecucion: workflow.last_run || 'No se ha ejecutado',
        }))
        downloadExcel(exportData, 'workflows')
    }

    const workflowList = [...localWorkflows, ...workflows]

    const activeStats = useMemo(() => ({
        total: workflowList.length,
        running: workflowList.filter((workflow: any) => workflow.state === 'running').length,
        failures: workflowList.filter((workflow: any) => workflow.state === 'failed').length,
    }), [workflowList])

    return (
        <div className="space-y-6 min-w-0">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">Automatización</h1>
                    <p className="text-gray-400 mt-2">Flujos, ejecución automática y control de reglas en un solo lugar.</p>
                </div>
                <button
                    onClick={handleExport}
                    className="inline-flex items-center gap-2 rounded-2xl bg-slate-700 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-600"
                >
                    <Download className="h-4 w-4" />
                    Descargar flujo
                </button>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {[
                    { label: 'Workflows totales', value: activeStats.total },
                    { label: 'En ejecución', value: activeStats.running },
                    { label: 'Fallos detectados', value: activeStats.failures },
                ].map((item) => (
                    <div key={item.label} className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                        <p className="text-sm uppercase tracking-[0.2em] text-sky-400">{item.label}</p>
                        <p className="mt-4 text-3xl font-semibold text-white">{item.value}</p>
                    </div>
                ))}
            </div>

            <div className="grid gap-6 lg:grid-cols-[0.75fr_1.25fr]">
                <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                    <div className="flex items-center justify-between">
                        <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Agregar workflow</p>
                        <Settings2 className="h-5 w-5 text-slate-300" />
                    </div>
                    <div className="mt-6 space-y-4">
                        <label className="space-y-2 text-sm text-gray-300">
                            Nombre del flujo
                            <input
                                type="text"
                                value={newWorkflowName}
                                onChange={(event) => setNewWorkflowName(event.target.value)}
                                className="w-full rounded-2xl border border-white/10 bg-slate-950/90 px-4 py-3 text-white outline-none focus:border-sky-500"
                            />
                        </label>
                        <button
                            onClick={createWorkflow}
                            className="inline-flex items-center gap-2 rounded-2xl bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500"
                        >
                            <Plus className="h-4 w-4" />
                            Guardar workflow
                        </button>
                        <p className="text-sm text-emerald-300">Los workflows locales se agregan al panel y pueden ejecutarse inmediatamente.</p>
                    </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                    <div className="flex items-center justify-between">
                        <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Última automatización</p>
                        <Sparkles className="h-5 w-5 text-slate-300" />
                    </div>
                    <div className="mt-6 space-y-4">
                        {workflowList.slice(0, 4).map((workflow: any) => (
                            <div key={workflow.id} className="rounded-3xl bg-slate-900/80 p-4">
                                <div className="flex items-center justify-between gap-4">
                                    <div>
                                        <p className="text-base font-semibold text-white">{workflow.name}</p>
                                        <p className="text-sm text-gray-400">Estado: {workflow.state}</p>
                                    </div>
                                    <button
                                        onClick={() => {
                                            setActiveWorkflow(workflow)
                                            executeMutation.mutate(workflow.id)
                                        }}
                                        className="inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-3 py-2 text-xs font-semibold text-white hover:bg-blue-500"
                                    >
                                        <Play className="h-3.5 w-3.5" />
                                        Ejecutar
                                    </button>
                                </div>
                                <p className="mt-3 text-sm text-gray-400">Última ejecución: {workflow.last_run || 'No registrado'}</p>
                            </div>
                        ))}
                    </div>
                    {executeMutation.isSuccess && (
                        <p className="mt-4 rounded-3xl bg-emerald-500/10 p-4 text-sm text-emerald-300">Workflow ejecutado correctamente.</p>
                    )}
                </div>
            </div>
        </div>
    )
}
