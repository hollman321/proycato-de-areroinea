"use client";

import ClientOnly from "@/components/ClientOnly";
import { Button } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { useToast } from "@/providers/ToastProvider";
import api from "@/services/api";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Activity,
  BarChart3,
  Clock,
  DollarSign,
  Plane,
  RefreshCw,
  ShieldCheck,
  TrendingUp,
  Users,
} from "lucide-react";
import { useMemo } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const CHART_COLORS = {
  ops: ["#38bdf8", "#fbbf24", "#10b981", "#f87171"],
};

type OperationRecord = {
  id: number;
  title: string;
  description?: string;
  client_id: number;
  status: string;
  category?: string;
  type: string;
  amount: number;
  created_at: string;
  updated_at?: string;
};

type PaginatedClients = {
  items: { id: number }[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
  };
};

type ServiceStatus = {
  status: string;
  message?: string;
  latency?: string;
};

type SystemHealthResponse = {
  api_gateway: ServiceStatus;
  database: ServiceStatus & { info?: Record<string, unknown> };
  services: {
    ia_engine: ServiceStatus;
  };
};

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const { success } = useToast();

  const { data: operationsResponse, isLoading: loadingOps } = useQuery({
    queryKey: ["dashboard-operations"],
    queryFn: async () =>
      (
        await api.get<{ operations: OperationRecord[] }>("/operations", {
          params: { limit: 50 },
        })
      ).data,
  });

  const { data: clientsResponse, isLoading: loadingClients } = useQuery({
    queryKey: ["dashboard-clients"],
    queryFn: async () =>
      (await api.get<PaginatedClients>("/pasajeros", { params: { limit: 1 } }))
        .data,
  });

  const { data: systemHealthData, isLoading: loadingSystem } = useQuery({
    queryKey: ["dashboard-system-health"],
    queryFn: async () =>
      (await api.get<SystemHealthResponse>("/health/system")).data,
  });

  const loading = loadingOps || loadingClients || loadingSystem;

  const operations = useMemo(
    () => operationsResponse?.operations ?? [],
    [operationsResponse],
  );

  const totalClients = clientsResponse?.pagination?.total ?? 0;

  const stats = useMemo(() => {
    const totalBalance = operations.reduce(
      (acc, operation) =>
        operation.type === "INCOME"
          ? acc + operation.amount
          : acc - operation.amount,
      0,
    );

    const activeOps = operations.filter(
      (operation) => operation.status === "IN_PROGRESS",
    ).length;
    return {
      balance: totalBalance,
      activeOps,
      totalClients,
      completed: operations.filter(
        (operation) => operation.status === "COMPLETED",
      ).length,
      totalOperations: operations.length,
    };
  }, [operations, totalClients]);

  const efficiency = useMemo(() => {
    if (stats.totalOperations === 0) return 0;
    return Number(((stats.completed / stats.totalOperations) * 100).toFixed(1));
  }, [stats.completed, stats.totalOperations]);

  const financeChartData = useMemo(() => {
    const grouped: Record<string, number> = {};
    operations
      .filter((item) => item.type === "INCOME")
      .forEach((item) => {
        const key = new Date(item.created_at).toLocaleDateString("es-ES", {
          day: "2-digit",
          month: "short",
        });
        grouped[key] = (grouped[key] || 0) + item.amount;
      });
    return Object.entries(grouped)
      .map(([name, amount]) => ({ name, amount }))
      .slice(-7);
  }, [operations]);

  const opsChartData = useMemo(() => {
    const counts = operations.reduce<Record<string, number>>((acc, op) => {
      acc[op.status] = (acc[op.status] || 0) + 1;
      return acc;
    }, {});

    return [
      { name: "Pendientes", value: counts["PENDING"] ?? 0 },
      { name: "En Proceso", value: counts["IN_PROGRESS"] ?? 0 },
      { name: "Completados", value: counts["COMPLETED"] ?? 0 },
      { name: "Cancelados", value: counts["CANCELLED"] ?? 0 },
    ];
  }, [operations]);

  const recentOperations = useMemo(() => {
    return [...operations]
      .sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      )
      .slice(0, 5)
      .map((operation) => ({
        id: operation.id,
        title: `${operation.title} - ${operation.type === "INCOME" ? "Ingreso" : "Gasto"}`,
        subtitle: operation.description || "Operación registrada",
        time: new Date(operation.created_at).toLocaleString("es-ES", {
          hour: "2-digit",
          minute: "2-digit",
          day: "2-digit",
          month: "long",
        }),
        status: operation.status,
      }));
  }, [operations]);

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat("es-ES", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(val);

  const apiStatus = systemHealthData?.api_gateway?.status ?? "Desconocido";
  const dbStatus = systemHealthData?.database?.status ?? "Desconocido";
  const iaStatus =
    systemHealthData?.services?.ia_engine?.status ?? "No disponible";

  const handleRefresh = () => {
    queryClient.invalidateQueries();
    success("Métricas actualizadas en tiempo real");
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Resumen Ejecutivo</h1>
          <p className="text-slate-400 mt-1">
            Operational Intelligence Center conectado a PostgreSQL.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            icon={
              <RefreshCw
                className={`h-4 w-4 ${loading ? "animate-spin" : ""}`}
              />
            }
            onClick={handleRefresh}
          >
            Actualizar Datos
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
        <StatCard
          title="Ingresos Totales"
          value={formatCurrency(stats.balance)}
          trend={{ value: 0, label: "real" }}
          icon={<DollarSign className="h-5 w-5 sm:h-6 sm:w-6" />}
          color="emerald"
          loading={loading}
        />
        <StatCard
          title="Operaciones Activas"
          value={stats.activeOps}
          trend={{ value: 0, label: "actual" }}
          icon={<Plane className="h-5 w-5 sm:h-6 sm:w-6" />}
          color="sky"
          loading={loading}
        />
        <StatCard
          title="Total Clientes"
          value={totalClients}
          icon={<Users className="h-5 w-5 sm:h-6 sm:w-6" />}
          color="violet"
          loading={loadingClients}
        />
        <StatCard
          title="Eficiencia"
          value={`${efficiency.toFixed(1)}%`}
          trend={{ value: efficiency, label: "completadas" }}
          icon={<Activity className="h-5 w-5 sm:h-6 sm:w-6" />}
          color="amber"
          loading={loading}
        />
      </div>

      <div className="grid gap-6 xl:gap-8 grid-cols-1 xl:grid-cols-2">
        <div className="rounded-3xl border border-white/5 bg-slate-900/50 p-6 sm:p-8 backdrop-blur-xl shadow-2xl flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-white">
                Tendencia de Flujo
              </h3>
              <p className="text-sm text-slate-400">
                Últimos ingresos por fecha
              </p>
            </div>
            <TrendingUp className="h-5 w-5 text-emerald-400" />
          </div>
          <div className="h-87.5 sm:h-100 w-full flex-1">
            <ClientOnly>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={financeChartData}>
                  <defs>
                    <linearGradient
                      id="colorAmount"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#ffffff05"
                    vertical={false}
                  />
                  <XAxis
                    dataKey="name"
                    stroke="#64748b"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    stroke="#64748b"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val) => `$${val}`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderRadius: "12px",
                      border: "1px solid #ffffff10",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="amount"
                    stroke="#0ea5e9"
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorAmount)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </ClientOnly>
          </div>
        </div>

        <div className="rounded-3xl border border-white/5 bg-slate-900/50 p-6 sm:p-8 backdrop-blur-xl shadow-2xl flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-white">
                Estado de Operaciones
              </h3>
              <p className="text-sm text-slate-400">
                Distribución de estados reales
              </p>
            </div>
            <BarChart3 className="h-5 w-5 text-sky-400" />
          </div>
          <div className="h-87.5 sm:h-100 w-full flex-1">
            <ClientOnly>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={opsChartData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#ffffff05"
                    vertical={false}
                  />
                  <XAxis
                    dataKey="name"
                    stroke="#64748b"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    stroke="#64748b"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip
                    cursor={{ fill: "#ffffff05" }}
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderRadius: "12px",
                      border: "1px solid #ffffff10",
                    }}
                  />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {opsChartData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={CHART_COLORS.ops[index % CHART_COLORS.ops.length]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </ClientOnly>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-3xl border border-white/5 bg-slate-900/50 p-6 backdrop-blur-xl shadow-2xl">
          <div className="flex items-center gap-2 mb-6">
            <Clock className="h-5 w-5 text-sky-400" />
            <h3 className="text-lg font-bold text-white">Actividad Reciente</h3>
          </div>
          <div className="space-y-4">
            {recentOperations.length > 0 ? (
              recentOperations.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5 group hover:bg-white/10 transition-colors"
                >
                  <div className="flex flex-col gap-1">
                    <p className="text-sm font-medium text-slate-200">
                      {item.title}
                    </p>
                    <p className="text-xs text-slate-500">{item.subtitle}</p>
                  </div>
                  <span className="text-xs text-slate-500">{item.time}</span>
                </div>
              ))
            ) : (
              <div className="p-4 rounded-2xl bg-white/5 border border-white/5 text-slate-400">
                No hay actividad reciente disponible.
              </div>
            )}
          </div>
        </div>

        <div className="rounded-3xl border border-white/5 bg-slate-900/50 p-6 backdrop-blur-xl shadow-2xl">
          <div className="flex items-center gap-2 mb-6">
            <ShieldCheck className="h-5 w-5 text-emerald-400" />
            <h3 className="text-lg font-bold text-white">Estado del Sistema</h3>
          </div>
          <div className="space-y-6">
            {[
              {
                name: "API Gateway",
                status: apiStatus,
                latency: systemHealthData?.api_gateway?.latency ?? "-",
              },
              {
                name: "PostgreSQL DB",
                status: dbStatus,
                latency: systemHealthData?.database?.latency ?? "-",
              },
              {
                name: "IA Engine",
                status: iaStatus,
                latency: systemHealthData?.services?.ia_engine?.latency ?? "-",
              },
            ].map((service) => (
              <div key={service.name} className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-300">
                    {service.name}
                  </span>
                  <span
                    className={`text-xs font-bold ${service.status === "online" || service.status === "En Línea" ? "text-emerald-400" : service.status === "Procesando" ? "text-amber-400" : "text-rose-400"}`}
                  >
                    {service.status}
                  </span>
                </div>
                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{
                      width:
                        service.status === "online" ||
                        service.status === "En Línea"
                          ? "100%"
                          : "40%",
                    }}
                    className="h-full bg-emerald-500/50"
                  />
                </div>
                <span className="text-[10px] text-slate-500">
                  Latencia: {service.latency}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
