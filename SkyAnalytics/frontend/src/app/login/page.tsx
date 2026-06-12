"use client";

import { Button } from "@/components/ui/Card";
import { useToast } from "@/providers/ToastProvider";
import api from "@/services/api";
import { useAuthStore } from "@/store/auth";
import { Lock, Mail } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LoginPage() {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { success, error } = useToast();
  const login = useAuthStore((state) => state.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.post("/auth/login", {
        email: formData.email,
        password: formData.password,
        remember_me: true,
      });
      const token = response.data?.access_token;
      if (!token) {
        throw new Error("No se recibió token de autenticación");
      }
      // Guardar token PRIMERO antes de hacer otra petición
      localStorage.setItem("auth-token", token);
      document.cookie = `auth-token=${token}; path=/`;

      // Ahora el interceptor puede usar el token
      const profileResponse = await api.get("/auth/me");
      login(profileResponse.data, token);
      success("Bienvenido de nuevo");
      router.push("/dashboard");
    } catch (err: any) {
      error(err.response?.data?.detail || "Credenciales inválidas");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="rounded-3xl border border-white/10 bg-slate-900/50 p-8 backdrop-blur-xl shadow-2xl">
          <h2 className="text-2xl font-bold text-white mb-6">Iniciar sesión</h2>

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input
                type="email"
                required
                className="w-full rounded-xl bg-slate-950 border border-white/10 p-3 pl-10 text-white focus:ring-2 focus:ring-sky-500/50"
                placeholder="ejemplo@correo.com"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
              />
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input
                type="password"
                required
                className="w-full rounded-xl bg-slate-950 border border-white/10 p-3 pl-10 text-white focus:ring-2 focus:ring-sky-500/50"
                placeholder="Contraseña"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
              />
            </div>

            <Button
              type="submit"
              className="w-full h-12 mt-4"
              loading={loading}
            >
              Iniciar sesión
            </Button>
          </form>

          <div className="mt-6 flex flex-col gap-3 text-sm text-slate-400">
            <Link href="/register" className="text-sky-400 hover:text-sky-300">
              Crear cuenta
            </Link>
            <Link
              href="/forgot-password"
              className="text-slate-300 hover:text-white"
            >
              ¿Olvidaste tu contraseña?
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
