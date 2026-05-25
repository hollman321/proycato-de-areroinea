'use client'

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { DollarSign, Plus, ArrowUpCircle, ArrowDownCircle, Search, Tag, Calendar, Trash2, Edit2, X, Download } from 'lucide-react'
import { StatCard } from '@/components/ui/StatCard'
import { Button } from '@/components/ui/Card'
import { useToast } from '@/providers/ToastProvider'
import { motion, AnimatePresence } from 'framer-motion'
import { formatDate } from '@/lib/utils'
import { downloadExcel } from '@/utils/export'
import axios from 'axios'

const CATEGORIES = ['Ventas', 'Servicios', 'Mantenimiento', 'Sueldos', 'Marketing', 'Infraestructura', 'Otros']

export default function FinanzasPage() {
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [editingTransaction, setEditingTransaction] = useState<any>(null)
    const [formData, setFormData] = useState({ type: 'INCOME', amount: '', category: 'Ventas', description: '', date: new Date().toISOString().split('T')[0] })

    const queryClient = useQueryClient()
    const { success, error, info } = useToast()

    // Data Fetching
    const { data: transactions, isLoading } = useQuery({
        queryKey: ['transactions'],
        queryFn: async () => (await axios.get('/api/finance')).data
    })

    // Balances Automáticos
    const { balance, incomes, expenses } = useMemo(() => {
        if (!transactions) return { balance: 0, incomes: 0, expenses: 0 }
        return transactions.reduce((acc: any, t: any) => {
            if (t.type === 'INCOME') acc.incomes += t.amount
            else acc.expenses += t.amount
            acc.balance = acc.incomes - acc.expenses
            return acc
        }, { balance: 0, incomes: 0, expenses: 0 })
    }, [transactions])

    const handleExport = () => {
        if (!transactions || transactions.length === 0) return error('No hay datos para exportar')
        info('Preparando reporte financiero...')
        const exportData = transactions.map((t: any) => ({
            ID: t.id,
            Tipo: t.type === 'INCOME' ? 'Ingreso' : 'Egreso',
            Monto: t.amount,
            Categoria: t.category,
            Descripcion: t.description,
            Fecha: formatDate(t.date)
        }))
        downloadExcel(exportData, 'reporte_financiero_skyanalytics')
        success('Reporte exportado exitosamente')
    }

    const saveMutation = useMutation({
        mutationFn: async (data: any) => {
            return editingTransaction
                ? axios.patch(`/api/finance/${editingTransaction.id}`, data)
                : axios.post('/api/finance', data)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['transactions'] })
            success(editingTransaction ? 'Transacción actualizada' : 'Transacción registrada')
            closeModal()
        },
        onError: () => error('Error al procesar la transacción')
    })

    const deleteMutation = useMutation({
        mutationFn: async (id: string) => axios.delete(`/api/finance/${id}`),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['transactions'] })
            success('Transacción eliminada')
        }
    })

    const openModal = (t?: any) => {
        if (t) {
            setEditingTransaction(t)
            setFormData({ type: t.type, amount: t.amount.toString(), category: t.category, description: t.description || '', date: new Date(t.date).toISOString().split('T')[0] })
        } else {
            setEditingTransaction(null)
            setFormData({ type: 'INCOME', amount: '', category: 'Ventas', description: '', date: new Date().toISOString().split('T')[0] })
        }
        setIsModalOpen(true)
    }

    const closeModal = () => setIsModalOpen(false)

    const formatCurrency = (val: number) =>
        new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'USD' }).format(val)

    return (
        <div className="space-y-8 w-full flex flex-col">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">Gestión Financiera</h1>
                    <p className="text-slate-400 mt-1">Control de ingresos, egresos y balances de operación.</p>
                </div>
                <div className="flex gap-3">
                    <Button variant="ghost" icon={<Download className="h-4 w-4" />} onClick={handleExport}>
                        Exportar
                    </Button>
                    <Button icon={<Plus className="h-4 w-4" />} onClick={() => openModal()}>
                        Nueva Transacción
                    </Button>
                </div>
            </div>

            <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                <StatCard title="Balance Total" value={formatCurrency(balance)} icon={<DollarSign className="h-6 w-6" />} color="sky" loading={isLoading} />
                <StatCard title="Ingresos" value={formatCurrency(incomes)} icon={<ArrowUpCircle className="h-6 w-6" />} color="emerald" loading={isLoading} />
                <StatCard title="Gastos" value={formatCurrency(expenses)} icon={<ArrowDownCircle className="h-6 w-6" />} color="rose" loading={isLoading} />
            </div>

            <div className="rounded-3xl border border-white/5 bg-slate-900/50 backdrop-blur-xl overflow-hidden shadow-2xl">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-white/5 text-slate-400 text-xs uppercase tracking-wider">
                                <th className="px-6 py-4 font-semibold">Concepto</th>
                                <th className="px-6 py-4 font-semibold">Categoría</th>
                                <th className="px-6 py-4 font-semibold">Fecha</th>
                                <th className="px-6 py-4 font-semibold">Monto</th>
                                <th className="px-6 py-4 font-semibold text-right">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {transactions?.map((t: any) => (
                                <tr key={t.id} className="hover:bg-white/[0.02] transition-colors group">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className={`h-10 w-10 rounded-xl flex items-center justify-center border border-white/5 ${t.type === 'INCOME' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                                                {t.type === 'INCOME' ? <ArrowUpCircle className="h-5 w-5" /> : <ArrowDownCircle className="h-5 w-5" />}
                                            </div>
                                            <div>
                                                <div className="font-medium text-white">{t.description || 'Sin descripción'}</div>
                                                <div className="text-xs text-slate-500 uppercase tracking-tighter">{t.type === 'INCOME' ? 'Ingreso' : 'Egreso'}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-300">
                                        <span className="flex items-center gap-1.5"><Tag className="h-3 w-3" /> {t.category}</span>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-400">
                                        <span className="flex items-center gap-1.5"><Calendar className="h-3 w-3" /> {formatDate(t.date)}</span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`font-bold ${t.type === 'INCOME' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                            {t.type === 'INCOME' ? '+' : '-'} {formatCurrency(t.amount)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button onClick={() => openModal(t)} className="p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-all"><Edit2 className="h-4 w-4" /></button>
                                            <button onClick={() => deleteMutation.mutate(t.id)} className="p-2 hover:bg-rose-500/10 rounded-lg text-slate-400 hover:text-rose-400 transition-all"><Trash2 className="h-4 w-4" /></button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <AnimatePresence>
                {isModalOpen && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" onClick={closeModal} />
                        <motion.div initial={{ opacity: 0, scale: 0.95, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95, y: 20 }} className="relative w-full max-w-md rounded-3xl border border-white/10 bg-slate-900 p-8 shadow-2xl">
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xl font-bold text-white">{editingTransaction ? 'Editar Transacción' : 'Nueva Transacción'}</h2>
                                <button onClick={closeModal} className="text-slate-400 hover:text-white"><X className="h-5 w-5" /></button>
                            </div>

                            <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); saveMutation.mutate(formData); }}>
                                <div className="flex p-1 bg-slate-950 rounded-xl border border-white/5">
                                    <button
                                        type="button"
                                        className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${formData.type === 'INCOME' ? 'bg-emerald-500 text-white' : 'text-slate-400 hover:text-white'}`}
                                        onClick={() => setFormData({ ...formData, type: 'INCOME' })}
                                    >Ingreso</button>
                                    <button
                                        type="button"
                                        className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${formData.type === 'EXPENSE' ? 'bg-rose-500 text-white' : 'text-slate-400 hover:text-white'}`}
                                        onClick={() => setFormData({ ...formData, type: 'EXPENSE' })}
                                    >Egreso</button>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Monto (USD)</label>
                                        <input type="number" step="0.01" required className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50" value={formData.amount} onChange={(e) => setFormData({ ...formData, amount: e.target.value })} />
                                    </div>
                                    <div>
                                        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Fecha</label>
                                        <input type="date" required className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50" value={formData.date} onChange={(e) => setFormData({ ...formData, date: e.target.value })} />
                                    </div>
                                </div>

                                <div>
                                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Categoría</label>
                                    <select required className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50" value={formData.category} onChange={(e) => setFormData({ ...formData, category: e.target.value })}>
                                        {CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                                    </select>
                                </div>

                                <div>
                                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Descripción / Notas</label>
                                    <textarea rows={2} className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} />
                                </div>

                                <div className="pt-4 flex gap-3">
                                    <Button type="button" variant="ghost" className="flex-1" onClick={closeModal}>Cancelar</Button>
                                    <Button type="submit" className="flex-1" loading={saveMutation.isPending}>{editingTransaction ? 'Actualizar' : 'Registrar'}</Button>
                                </div>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    )
}