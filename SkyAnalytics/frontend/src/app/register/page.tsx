'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { User, Mail, Lock, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/Card'
import { useToast } from '@/providers/ToastProvider'
import api from '@/services/api'

export default function RegisterPage() {
    const [formData, setFormData] = useState({ full_name: '', email: '', password: '' })
    const [loading, setLoading] = useState(false)
    const router = useRouter()
    const { success, error } = useToast()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        try {
            await api.post('/auth/register', formData)
            success('Cuenta creada exitosamente. Ya puedes iniciar sesión.')
            router.push('/login')
        } catch (err: any) {
            error(err.response?.data?.detail || 'Error en el registro')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
            <div className="w-full max-w-md space-y-8">
                <Link href="/login" className="inline-flex items-center text-sm text-slate-400 hover:text-white transition-colors">
                    <ArrowLeft className="mr-2 h-4 w-4" /> Volver al login
                </Link>

                <div className="rounded-3xl border border-white/10 bg-slate-900/50 p-8 backdrop-blur-xl shadow-2xl">
                    <h2 className="text-2xl font-bold text-white mb-6">Crear Cuenta Administrativa</h2>

                    <form className="space-y-4" onSubmit={handleSubmit}>
                        <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
                            <input
                                type="text" required
                                className="w-full rounded-xl bg-slate-950 border border-white/10 p-3 pl-10 text-white focus:ring-2 focus:ring-sky-500/50"
                                placeholder="Nombre completo"
                                value={formData.full_name}
                                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                            />
                        </div>
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
                            <input
                                type="email" required
                                className="w-full rounded-xl bg-slate-950 border border-white/10 p-3 pl-10 text-white focus:ring-2 focus:ring-sky-500/50"
                                placeholder="Correo corporativo"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            />
                        </div>
                        <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
                            <input
                                type="password" required
                                minLength={8}
                                className="w-full rounded-xl bg-slate-950 border border-white/10 p-3 pl-10 text-white focus:ring-2 focus:ring-sky-500/50"
                                placeholder="Contraseña segura"
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            />
                        </div>

                        <Button type="submit" className="w-full h-12 mt-4" loading={loading}>
                            Registrar cuenta
                        </Button>
                    </form>
                </div>
            </div>
        </div>
    )
}
