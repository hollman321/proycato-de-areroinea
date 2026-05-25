'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Users, UserPlus, Search, Filter, Trash2, Edit2, Mail, Phone, Building2, X, Loader2 } from 'lucide-react'
import { StatCard } from '@/components/ui/StatCard'
import { Button } from '@/components/ui/Card'
import { useToast } from '@/providers/ToastProvider'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'

interface Client {
    id: string
    name: string
    email: string
    phone?: string
    company?: string
    status: string
}

export default function ClientesPage() {
    const [searchTerm, setSearchTerm] = useState('')
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [editingClient, setEditingClient] = useState<Client | null>(null)
    const [formData, setFormData] = useState({ name: '', email: '', phone: '', company: '' })

    const queryClient = useQueryClient()
    const { success, error, info } = useToast()

    // 1. Obtener Clientes
    const { data: clients, isLoading } = useQuery({
        queryKey: ['clients'],
        queryFn: async () => {
            const res = await axios.get('/api/clients')
            return res.data
        }
    })

    // 2. Mutación para Crear/Editar
    const saveMutation = useMutation({
        mutationFn: async (data: any) => {
            if (editingClient) {
                return axios.patch(`/api/clients/${editingClient.id}`, data)
            }
            return axios.post('/api/clients', data)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['clients'] })
            success(editingClient ? 'Cliente actualizado' : 'Cliente creado con éxito')
            closeModal()
        },
        onError: (err: any) => {
            const message = err.response?.data?.error || 'Ocurrió un error al guardar los datos'
            error(message)
        }
    })

    const openModal = (client?: Client) => {
        if (client) {
            setEditingClient(client)
            setFormData({ name: client.name, email: client.email, phone: client.phone || '', company: client.company || '' })
        } else {
            setEditingClient(null)
            setFormData({ name: '', email: '', phone: '', company: '' })
        }
        setIsModalOpen(true)
    }

    const closeModal = () => setIsModalOpen(false)

    // 3. Mutación para Eliminar
    const deleteMutation = useMutation({
        mutationFn: async (id: string) => axios.delete(`/api/clients/${id}`),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['clients'] })
            success('Cliente eliminado correctamente')
        },
        onError: () => error('No se pudo eliminar el cliente')
    })

    const filteredClients = clients?.filter((c: Client) =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.email.toLowerCase().includes(searchTerm.toLowerCase())
    )

    return (
        <div className="space-y-8 w-full flex flex-col">
            {/* Header & Acciones Rápidas */}
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">Gestión de Clientes</h1>
                    <p className="text-slate-400 mt-1">Administra la base de datos central de pasajeros y corporativos.</p>
                </div>
                <Button
                    icon={<UserPlus className="h-4 w-4" />}
                    onClick={() => openModal()}
                >
                    Nuevo Cliente
                </Button>
            </div>

            {/* KPIs Rápidos */}
            <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                <StatCard
                    title="Total Clientes"
                    value={clients?.length || 0}
                    icon={<Users className="h-6 w-6" />}
                    color="sky"
                    loading={isLoading}
                />
                <StatCard
                    title="Nuevos (30d)"
                    value="+12"
                    subtitle="Incremento del 8%"
                    icon={<UserPlus className="h-6 w-6" />}
                    color="emerald"
                    loading={isLoading}
                />
                <StatCard
                    title="Empresas"
                    value={clients?.filter((c: Client) => c.company).length || 0}
                    icon={<Building2 className="h-6 w-6" />}
                    color="violet"
                    loading={isLoading}
                />
            </div>

            {/* Tabla Enterprise */}
            <div className="rounded-3xl border border-white/5 bg-slate-900/50 backdrop-blur-xl overflow-hidden shadow-2xl">
                <div className="p-6 border-b border-white/5 flex flex-col sm:flex-row gap-4 justify-between items-center">
                    <div className="relative w-full sm:max-w-xs">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                        <input
                            type="text"
                            placeholder="Buscar por nombre o email..."
                            className="w-full bg-slate-950/50 border border-white/10 rounded-xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/50 transition-all"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div className="flex gap-2 w-full sm:w-auto">
                        <Button variant="ghost" size="sm" icon={<Filter className="h-4 w-4" />}>Filtros</Button>
                        <Button variant="ghost" size="sm" onClick={() => queryClient.invalidateQueries({ queryKey: ['clients'] })}>Actualizar</Button>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-white/5 text-slate-400 text-xs uppercase tracking-wider">
                                <th className="px-6 py-4 font-semibold">Cliente</th>
                                <th className="px-6 py-4 font-semibold">Contacto</th>
                                <th className="px-6 py-4 font-semibold">Empresa</th>
                                <th className="px-6 py-4 font-semibold">Estado</th>
                                <th className="px-6 py-4 font-semibold text-right">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {isLoading ? (
                                [...Array(5)].map((_, i) => (
                                    <tr key={i} className="animate-pulse">
                                        <td colSpan={5} className="px-6 py-4"><div className="h-8 bg-white/5 rounded-lg w-full" /></td>
                                    </tr>
                                ))
                            ) : filteredClients?.map((client: Client) => (
                                <tr key={client.id} className="hover:bg-white/[0.02] transition-colors group">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="h-10 w-10 rounded-full bg-sky-500/10 flex items-center justify-center text-sky-400 font-bold border border-sky-500/20">
                                                {client.name.charAt(0)}
                                            </div>
                                            <div className="font-medium text-white">{client.name}</div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="text-sm space-y-1">
                                            <div className="flex items-center gap-2 text-slate-300"><Mail className="h-3 w-3" /> {client.email}</div>
                                            <div className="flex items-center gap-2 text-slate-500"><Phone className="h-3 w-3" /> {client.phone || 'N/A'}</div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-300">
                                        {client.company || <span className="text-slate-600">—</span>}
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                            {client.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button
                                                onClick={() => openModal(client)}
                                                className="p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-all"
                                            >
                                                <Edit2 className="h-4 w-4" />
                                            </button>
                                            <button
                                                onClick={() => deleteMutation.mutate(client.id)}
                                                className="p-2 hover:bg-rose-500/10 rounded-lg text-slate-400 hover:text-rose-400 transition-all"
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modal de Creación/Edición */}
            <AnimatePresence>
                {isModalOpen && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                            className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
                            onClick={closeModal}
                        />
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="relative w-full max-w-md rounded-3xl border border-white/10 bg-slate-900 p-8 shadow-2xl"
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xl font-bold text-white">{editingClient ? 'Editar Cliente' : 'Nuevo Cliente'}</h2>
                                <button onClick={closeModal} className="text-slate-400 hover:text-white"><X className="h-5 w-5" /></button>
                            </div>

                            <form className="space-y-4" onSubmit={(e) => {
                                e.preventDefault()
                                saveMutation.mutate(formData)
                            }}>
                                <div>
                                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Nombre Completo</label>
                                    <input
                                        type="text" required
                                        className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Email Corporativo</label>
                                    <input
                                        type="email" required
                                        className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Teléfono</label>
                                        <input
                                            type="text"
                                            className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                                            value={formData.phone}
                                            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Empresa</label>
                                        <input
                                            type="text"
                                            className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                                            value={formData.company}
                                            onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <div className="pt-4 flex gap-3">
                                    <Button
                                        type="button" variant="ghost" className="flex-1"
                                        onClick={closeModal}
                                    >
                                        Cancelar
                                    </Button>
                                    <Button
                                        type="submit" className="flex-1"
                                        loading={saveMutation.isPending}
                                    >
                                        {editingClient ? 'Actualizar' : 'Guardar'}
                                    </Button>
                                </div>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    )
}