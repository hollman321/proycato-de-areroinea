'use client'

import { useState } from 'react'
import { FileText, Download, Table, Users, Plane, DollarSign, FileDown, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/Card'
import { useToast } from '@/providers/ToastProvider'
import { downloadExcel, downloadPDF } from '@/utils/export'
import axios from 'axios'
import { formatDate } from '@/lib/utils'

const REPORT_TYPES = [
    { id: 'finance', name: 'Finanzas y Transacciones', icon: DollarSign, color: 'text-emerald-400', bg: 'bg-emerald-500/10', description: 'Historial de ingresos, egresos y balances mensuales.' },
    { id: 'clients', name: 'Cartera de Clientes', icon: Users, color: 'text-sky-400', bg: 'bg-sky-500/10', description: 'Listado completo de clientes activos, empresas y contactos.' },
    { id: 'operations', name: 'Operaciones Aéreas', icon: Plane, color: 'text-violet-400', bg: 'bg-violet-500/10', description: 'Seguimiento de vuelos, estados y operadores asignados.' },
]

export default function ReportesPage() {
    const [loading, setLoading] = useState<string | null>(null)
    const { success, error, info } = useToast()

    const handleExport = async (type: string, format: 'pdf' | 'excel') => {
        const loadingKey = `${type}-${format}`
        setLoading(loadingKey)
        info(`Generando reporte de ${type}...`)

        try {
            const endpoint = `/api/${type === 'finance' ? 'finance' : type === 'clients' ? 'clients' : 'operations'}`
            const response = await axios.get(endpoint)
            const data = response.data

            if (format === 'excel') {
                const exportData = data.map((item: any) => {
                    if (type === 'finance') return {
                        ID: item.id,
                        Tipo: item.type === 'INCOME' ? 'Ingreso' : 'Egreso',
                        Monto: item.amount,
                        Categoria: item.category,
                        Descripcion: item.description,
                        Fecha: formatDate(item.date)
                    }
                    if (type === 'clients') return {
                        ID: item.id,
                        Nombre: item.name,
                        Email: item.email,
                        Empresa: item.company,
                        Estado: item.status,
                        Registro: formatDate(item.createdAt)
                    }
                    if (type === 'operations') return {
                        ID: item.id,
                        Titulo: item.title,
                        Cliente: item.client?.name,
                        Estado: item.status,
                        Fecha: formatDate(item.createdAt)
                    }
                })
                downloadExcel(exportData, `reporte_${type}`)
            } else {
                let title = ''
                let headers: string[] = []
                let rows: any[][] = []

                if (type === 'finance') {
                    title = 'Reporte Consolidado de Finanzas'
                    headers = ['REF ID', 'TIPO', 'MONTO', 'CATEGORÍA', 'FECHA']
                    rows = data.map((t: any) => [t.id.slice(-6).toUpperCase(), t.type, `$${t.amount}`, t.category, formatDate(t.date)])
                } else if (type === 'clients') {
                    title = 'Reporte de Base de Datos de Clientes'
                    headers = ['NOMBRE', 'EMAIL', 'EMPRESA', 'ESTADO']
                    rows = data.map((c: any) => [c.name, c.email, c.company || '-', c.status])
                } else {
                    title = 'Reporte Operacional de Tráfico'
                    headers = ['TÍTULO', 'CLIENTE', 'ESTADO', 'FECHA']
                    rows = data.map((o: any) => [o.title, o.client?.name, o.status, formatDate(o.createdAt)])
                }
                downloadPDF(title, headers, rows, `reporte_${type}`)
            }
            success(`Reporte ${format.toUpperCase()} generado correctamente`)
        } catch (err) {
            error('Error al generar el reporte. Verifique la conexión con el servidor.')
        } finally {
            setLoading(null)
        }
    }

    return (
        <div className="space-y-8">
            <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-2xl bg-sky-500/10 flex items-center justify-center border border-sky-500/20">
                    <FileText className="h-6 w-6 text-sky-400" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-white">Centro de Reportes</h1>
                    <p className="text-slate-400 mt-1">Exportación oficial de datos operacionales y financieros.</p>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {REPORT_TYPES.map((report) => (
                    <div key={report.id} className="rounded-3xl border border-white/5 bg-slate-900/50 p-6 backdrop-blur-xl shadow-2xl transition-all hover:bg-slate-900/80">
                        <div className={`h-12 w-12 rounded-2xl ${report.bg} flex items-center justify-center mb-4`}>
                            <report.icon className={`h-6 w-6 ${report.color}`} />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-2">{report.name}</h3>
                        <p className="text-sm text-slate-400 mb-6">{report.description}</p>

                        <div className="flex flex-col gap-3">
                            <Button
                                variant="secondary" icon={<Table className="h-4 w-4" />}
                                loading={loading === `${report.id}-excel`}
                                onClick={() => handleExport(report.id, 'excel')}
                            >Generar Excel (.xlsx)</Button>
                            <Button
                                variant="ghost" icon={<FileDown className="h-4 w-4" />}
                                loading={loading === `${report.id}-pdf`}
                                onClick={() => handleExport(report.id, 'pdf')}
                            >Exportar PDF (.pdf)</Button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}