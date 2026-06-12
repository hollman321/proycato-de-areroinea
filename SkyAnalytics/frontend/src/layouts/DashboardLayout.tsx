"use client";

// ChatIA removed — assistant UI disabled in layout
import { useAuthStore } from "@/store/auth";
import { AnimatePresence, motion } from "framer-motion";
import {
  BarChart3,
  Briefcase,
  DollarSign,
  FileText,
  LogOut,
  Menu,
  Plane,
  Users,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const navigation = [
  {
    section: "Vistas",
    items: [
      { name: "Resumen Ejecutivo", href: "/dashboard", icon: BarChart3 },
      { name: "Operaciones", href: "/dashboard/operaciones", icon: Briefcase },
      { name: "Clientes", href: "/dashboard/clientes", icon: Users },
      { name: "Finanzas", href: "/dashboard/finanzas", icon: DollarSign },
      { name: "Ejecutivo", href: "/dashboard/ejecutivo", icon: BarChart3 },
    ],
  },
  {
    section: "Administración",
    items: [
      { name: "Reportes", href: "/dashboard/reportes", icon: FileText },
    ],
  },
];

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    setSidebarOpen(false);
    router.replace("/login");
  };

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 1024);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 overflow-x-hidden flex">
      <AnimatePresence>
        {sidebarOpen && isMobile && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-60 bg-slate-950/80 backdrop-blur-sm lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      <motion.div
        className={`fixed left-0 top-0 z-70 flex h-full w-72 flex-col bg-slate-900 border-r border-white/5 transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-20 shrink-0 items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-sky-500 flex items-center justify-center">
              <Plane className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight">SkyAnalytics</h1>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="text-gray-400 hover:text-white lg:hidden"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <nav className="flex-1 min-h-0 px-4 pb-4 space-y-6 overflow-y-auto">
          {navigation.map((group) => (
            <div key={group.section} className="mb-6">
              <p className="px-3 pb-2 text-xs uppercase tracking-[0.3em] text-slate-400">
                {group.section}
              </p>
              <ul className="space-y-2">
                {group.items.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <li key={item.name}>
                      <Link
                        href={item.href}
                        className={`flex items-center rounded-xl px-4 py-3 text-sm font-medium transition-all ${
                          isActive
                            ? "bg-sky-500/10 text-sky-400 border border-sky-500/20"
                            : "text-slate-400 hover:bg-white/5 hover:text-white"
                        }`}
                        onClick={() => setSidebarOpen(false)}
                      >
                        <item.icon className="mr-3 h-5 w-5" />
                        {item.name}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        <div className="shrink-0 border-t border-white/5 p-4">
          <div className="rounded-2xl bg-white/5 p-4 border border-white/5 mb-3">
            <p className="text-sm font-semibold truncate">
              {user?.full_name || user?.email}
            </p>
            <p className="mt-1 text-xs text-gray-400 capitalize">
              {user?.role}
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-rose-500/10 px-4 py-3 text-sm font-semibold text-rose-400 transition hover:bg-rose-500/20 border border-rose-500/20"
          >
            <LogOut className="h-4 w-4" />
            Cerrar sesión
          </button>
        </div>
      </motion.div>

      <div className="flex-1 flex flex-col min-w-0 lg:pl-72">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between gap-4 bg-slate-950/80 backdrop-blur-md px-4 sm:px-6 lg:px-8 border-b border-white/5">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 text-slate-400 hover:text-white lg:hidden rounded-lg hover:bg-white/5"
          >
            <Menu className="h-6 w-6" />
          </button>
          <div className="flex-1" />
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex flex-col text-right">
              <span className="text-sm font-medium">
                {user?.full_name || user?.email}
              </span>
              <span className="text-xs text-slate-500 capitalize">
                {user?.role}
              </span>
            </div>
            <button
              onClick={handleLogout}
              aria-label="Cerrar sesion"
              className="p-2 text-slate-400 hover:text-rose-400 transition-colors rounded-lg hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </header>

        <main className="p-4 sm:p-6 lg:p-8 xl:p-10 w-full min-h-[calc(100vh-64px)] flex flex-col">
          {children}
        </main>
      </div>

      {/* Chat IA Assistant removed */}
    </div>
  );
}
