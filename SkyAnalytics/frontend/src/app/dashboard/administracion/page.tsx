'use client'

import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ShieldCheck, UserPlus, Search, Download, Lock, Users } from 'lucide-react'
import api, { getWithFallback } from '@/services/api'
import { mockAdminUsers } from '@/services/mockData'
import { downloadExcel } from '@/utils/export'

export default function AdministracionPage() {
    const queryClient = useQueryClient()
    const [search, setSearch] = useState('')
    const [selectedUser, setSelectedUser] = useState<any>(null)
    const [form, setForm] = useState({ nombre: '', correo: '', rol: 'admin' })

    const { data: users } = useQuery({
        queryKey: ['administracion-users'],
        queryFn: async () => {
            const response = await api.get('/admin/db/users')
            return (response.data.usuarios || []).map((user: any) => ({
                id: user.id,
                nombre_completo: user.full_name,
                correo: user.email,
                role: user.role,
                is_active: user.is_active,
            }))
        },
        staleTime: 90000,
    })

    const createMutation = useMutation({
        mutationFn: async (payload: any) => {
            const response = await api.post('/auth/register', payload)
            return response.data
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['administracion-users'] })
            setForm({ nombre: '', correo: '', rol: 'admin' })
        },
    })

    const updateMutation = useMutation({
        mutationFn: async (payload: any) => {
            const response = await api.put(`/admin/users/${selectedUser?.id}/active`, payload)
            return response.data
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['administracion-users'] })
            setSelectedUser(null)
        },
    })

    const handleCreate = () => {
        createMutation.mutate({
            nombre_completo: form.nombre,
            correo: form.correo,
            rol: form.rol,
        })
    }

    const handleToggleActive = () => {
        if (!selectedUser) return
        updateMutation.mutate({ is_active: !selectedUser.is_active })
    }

    const filteredUsers = (users || []).filter((user: any) =>
        `${user.nombre_completo} ${user.correo}`.toLowerCase().includes(search.toLowerCase())
    )

    const handleExport = () => {
        downloadExcel(filteredUsers.map((user: any) => ({
            Nombre: user.nombre_completo,
            Correo: user.correo,
            Rol: user.role || 'N/A',
            Activo: user.is_active ? 'Sí' : 'No',
        })), 'usuarios_admin')
    }

    useEffect(() => {
        if (selectedUser) {
            setForm({
                nombre: selectedUser.nombre_completo,
                correo: selectedUser.correo,
                rol: selectedUser.role || 'admin',
            })
        }
    }, [selectedUser])

    return (
        <div className="space-y-6 min-w-0">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">Administración</h1>
                    <p className="text-gray-400 mt-2">Control de usuarios, roles y configuración operativa del portal.</p>
                </div>
                <button
                    onClick={handleExport}
                    className="inline-flex items-center gap-2 rounded-2xl bg-slate-700 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-600"
                >
                    <Download className="h-4 w-4" />
                    Exportar usuarios
                </button>
            </div>

            <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
                <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                        <div className="flex items-center gap-3 rounded-3xl bg-slate-900/80 px-4 py-3">
                            <Search className="h-4 w-4 text-sky-400" />
                            <input
                                type="text"
                                placeholder="Buscar usuario"
                                value={search}
                                onChange={(event) => setSearch(event.target.value)}
                                className="w-full bg-transparent text-white outline-none placeholder:text-gray-500"
                            />
                        </div>
                        <button
                            onClick={() => {
                                setSelectedUser(null)
                                setForm({ nombre: '', correo: '', rol: 'admin' })
                            }}
                            className="inline-flex items-center gap-2 rounded-2xl bg-slate-700 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-600"
                        >
                            <UserPlus className="h-4 w-4" />
                            Nuevo usuario
                        </button>
                    </div>

                    <div className="mt-6 overflow-x-auto rounded-3xl border border-white/10 bg-slate-950/70">
                        <table className="min-w-[720px] w-full border-collapse text-left text-sm text-gray-200">
                            <thead className="bg-slate-900/80 text-xs uppercase tracking-wider text-gray-400">
                                <tr>
                                    <th className="px-4 py-4">Nombre</th>
                                    <th className="px-4 py-4">Correo</th>
                                    <th className="px-4 py-4">Rol</th>
                                    <th className="px-4 py-4">Activo</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredUsers.map((user: any) => (
                                    <tr key={user.id} className="border-t border-white/5 hover:bg-white/5 cursor-pointer" onClick={() => setSelectedUser(user)}>
                                        <td className="px-4 py-4 text-white">{user.nombre_completo}</td>
                                        <td className="px-4 py-4">{user.correo}</td>
                                        <td className="px-4 py-4">{user.role || 'admin'}</td>
                                        <td className="px-4 py-4">{user.is_active ? 'Sí' : 'No'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-6 shadow-xl">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm uppercase tracking-[0.2em] text-sky-400">Panel de usuario</p>
                            <p className="mt-2 text-gray-400">Crea usuarios, ajusta roles y públicos permisos.</p>
                        </div>
                        <Users className="h-5 w-5 text-slate-300" />
                    </div>

                    <div className="mt-6 space-y-4">
                        <div className="rounded-3xl bg-slate-900/80 p-4">
                            <p className="text-sm text-gray-400">Nombre</p>
                            <input
                                type="text"
                                value={form.nombre}
                                onChange={(event) => setForm((current) => ({ ...current, nombre: event.target.value }))}
                                className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/90 px-4 py-3 text-white outline-none focus:border-sky-500"
                            />
                        </div>
                        <div className="rounded-3xl bg-slate-900/80 p-4">
                            <p className="text-sm text-gray-400">Correo</p>
                            <input
                                type="email"
                                value={form.correo}
                                onChange={(event) => setForm((current) => ({ ...current, correo: event.target.value }))}
                                className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/90 px-4 py-3 text-white outline-none focus:border-sky-500"
                            />
                        </div>
                        <div className="rounded-3xl bg-slate-900/80 p-4">
                            <p className="text-sm text-gray-400">Rol</p>
                            <select
                                value={form.rol}
                                onChange={(event) => setForm((current) => ({ ...current, rol: event.target.value }))}
                                className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/90 px-4 py-3 text-white outline-none focus:border-sky-500"
                            >
                                <option value="admin">Administrador</option>
                                <option value="manager">Manager</option>
                                <option value="viewer">Viewer</option>
                            </select>
                        </div>
                        <div className="flex flex-wrap gap-3">
                            <button
                                onClick={handleCreate}
                                className="inline-flex items-center gap-2 rounded-2xl bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500"
                            >
                                <UserPlus className="h-4 w-4" />
                                Guardar usuario
                            </button>
                            {selectedUser && (
                                <button
                                    onClick={handleToggleActive}
                                    className="inline-flex items-center gap-2 rounded-2xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
                                >
                                    <ShieldCheck className="h-4 w-4" />
                                    {selectedUser.is_active ? 'Desactivar' : 'Activar'}
                                </button>
                            )}
                        </div>
                        {updateMutation.isSuccess && <p className="text-sm text-emerald-300">Estado de usuario actualizado.</p>}
                        {createMutation.isSuccess && <p className="text-sm text-emerald-300">Usuario creado correctamente.</p>}
                    </div>
                </div>
            </div>
        </div>
    )
}
