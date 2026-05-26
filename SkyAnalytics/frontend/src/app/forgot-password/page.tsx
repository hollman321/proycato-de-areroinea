'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Mail, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/Card'
import { useToast } from '@/providers/ToastProvider'
import api from '@/services/api'

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('')
    const [loading, setLoading] = useState(false)
    const router = useRouter()
    const { success, error } = useToast()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        try {
            await api.post('/auth/forgot-password', { email })
            success('Si el correo existe, recibirás instrucciones en breve.')
            router.push('/login')
        } catch (err: any) {
            error(err.response?.data?.detail || 'Error al solicitar recuperación')
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
                    <h2 className="text-2xl font-bold text-white mb-6">Recuperación de contraseña</h2>

                    <form className="space-y-4" onSubmit={handleSubmit}>
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
                            <input
                                type="email" required
                                className="w-full rounded-xl bg-slate-950 border border-white/10 p-3 pl-10 text-white focus:ring-2 focus:ring-sky-500/50"
                                placeholder="Correo electrónico"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>

                        <Button type="submit" className="w-full h-12 mt-4" loading={loading}>
                            Enviar instrucciones
                        </Button>
                    </form>
                </div>
            </div>
        </div>
    )
}
