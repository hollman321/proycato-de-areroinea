"use client";

import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, AlertTriangle, CheckCircle, Info, X } from "lucide-react";
import React from "react";

type ToastType = "success" | "error" | "warning" | "info";

interface ToastItem {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType, duration?: number) => void;
  success: (message: string) => void;
  error: (message: string) => void;
  warning: (message: string) => void;
  info: (message: string) => void;
}

const ToastContext = React.createContext<ToastContextType | undefined>(
  undefined,
);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<ToastItem[]>([]);

  const removeToast = React.useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = React.useCallback(
    (message: string, type: ToastType = "info", duration = 4000) => {
      const id = Math.random().toString(36).substring(2, 9);
      setToasts((prev) => [...prev, { id, message, type, duration }]);

      if (duration > 0) {
        setTimeout(() => {
          removeToast(id);
        }, duration);
      }
    },
    [removeToast],
  );

  const success = (msg: string) => showToast(msg, "success");
  const error = (msg: string) => showToast(msg, "error");
  const warning = (msg: string) => showToast(msg, "warning");
  const info = (msg: string) => showToast(msg, "info");

  const icons = {
    success: <CheckCircle className="h-5 w-5 text-emerald-400" />,
    error: <AlertCircle className="h-5 w-5 text-rose-400" />,
    warning: <AlertTriangle className="h-5 w-5 text-amber-400" />,
    info: <Info className="h-5 w-5 text-sky-400" />,
  } as const;

  const styles = {
    success: "border-emerald-500/30 bg-emerald-500/10",
    error: "border-rose-500/30 bg-rose-500/10",
    warning: "border-amber-500/30 bg-amber-500/10",
    info: "border-sky-500/30 bg-sky-500/10",
  } as const;

  return (
    <ToastContext.Provider value={{ showToast, success, error, warning, info }}>
      {children}
      <div className="fixed right-4 top-20 z-100 flex w-[calc(100vw-2rem)] max-w-sm flex-col gap-3 sm:w-auto">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, y: -16, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -16, scale: 0.95 }}
              className={`rounded-2xl border p-4 shadow-xl backdrop-blur-xl ${styles[t.type]}`}
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  {icons[t.type]}
                  <p className="text-sm font-medium text-white">{t.message}</p>
                </div>
                <button
                  onClick={() => removeToast(t.id)}
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = React.useContext(ToastContext);
  if (!context) throw new Error("useToast debe usarse dentro de ToastProvider");
  return context;
}
