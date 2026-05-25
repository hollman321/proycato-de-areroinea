'use client'

import { ReactNode } from 'react'
import { motion } from 'framer-motion'

interface ModalProps {
    open: boolean
    title: string
    onClose: () => void
    children: ReactNode
    footer?: ReactNode
}

export function Modal({ open, title, onClose, children, footer }: ModalProps) {
    if (!open) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4 py-6">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="w-full max-w-3xl overflow-hidden rounded-3xl border border-white/10 bg-slate-950 shadow-2xl"
            >
                <div className="flex items-center justify-between border-b border-white/10 px-6 py-4">
                    <h2 className="text-lg font-semibold text-white">{title}</h2>
                    <button
                        type="button"
                        onClick={onClose}
                        className="rounded-full bg-white/10 px-3 py-2 text-sm text-gray-300 transition hover:bg-white/20"
                    >
                        Cerrar
                    </button>
                </div>
                <div className="px-6 py-5 text-sm text-gray-200">{children}</div>
                {footer && <div className="border-t border-white/10 px-6 py-4">{footer}</div>}
            </motion.div>
        </div>
    )
}
