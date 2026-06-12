"use client";

import { Button } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { formatDate } from "@/lib/utils";
import { useToast } from "@/providers/ToastProvider";
import api from "@/services/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Edit2,
  Plane,
  Plus,
  Trash2,
  X,
} from "lucide-react";
import { useState } from "react";

const STATUS_OPTIONS = [
  {
    value: "PENDING",
    label: "Pendiente",
    color: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  },
  {
    value: "IN_PROGRESS",
    label: "En Proceso",
    color: "bg-sky-500/10 text-sky-400 border-sky-500/20",
  },
  {
    value: "COMPLETED",
    label: "Completado",
    color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  },
  {
    value: "CANCELLED",
    label: "Cancelado",
    color: "bg-rose-500/10 text-rose-400 border-rose-500/20",
  },
];

export default function OperacionesPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingOp, setEditingOp] = useState<any>(null);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    client_id: "",
    status: "PENDING",
    category: "Operación",
    type: "INCOME",
    amount: 0,
  });

  const queryClient = useQueryClient();
  const { success, error } = useToast();

  // Data Fetching
  const { data: operationsResponse, isLoading } = useQuery({
    queryKey: ["operations"],
    queryFn: async () =>
      (await api.get("/operations/", { params: { limit: 100 } })).data,
  });

  const { data: clientsResponse } = useQuery({
    queryKey: ["clients-list"],
    queryFn: async () =>
      (await api.get("/pasajeros", { params: { limit: 100 } })).data,
  });

  const saveMutation = useMutation({
    mutationFn: async (data: any) => {
      return editingOp
        ? api.put(`/operations/${editingOp.id}`, data)
        : api.post("/operations/", data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["operations"] });
      success(editingOp ? "Operación actualizada" : "Operación registrada");
      closeModal();
    },
    onError: () => error("Error al procesar la operación"),
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => api.delete(`/operations/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["operations"] });
      success("Operación eliminada");
    },
  });

  const operations = operationsResponse?.operations || [];
  const clients = clientsResponse?.items || [];
  const clientMap = new Map<number, string>(
    clients.map((client: any) => [client.id, client.nombre_completo]),
  );

  const openModal = (op?: any) => {
    if (op) {
      setEditingOp(op);
      setFormData({
        title: op.title,
        description: op.description || "",
        client_id: op.client_id?.toString() || "",
        status: op.status,
        category: op.category || "Operación",
        type: op.type || "INCOME",
        amount: op.amount || 0,
      });
    } else {
      setEditingOp(null);
      setFormData({
        title: "",
        description: "",
        client_id: "",
        status: "PENDING",
        category: "Operación",
        type: "INCOME",
        amount: 0,
      });
    }
    setIsModalOpen(true);
  };

  const closeModal = () => setIsModalOpen(false);

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">
            Centro de Operaciones
          </h1>
          <p className="text-slate-400 mt-1">
            Monitoreo y gestión de flujos logísticos en tiempo real.
          </p>
        </div>
        <Button icon={<Plus className="h-4 w-4" />} onClick={() => openModal()}>
          Nueva Operación
        </Button>
      </div>

      <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <StatCard
          title="Operaciones Activas"
          value={
            operations?.filter((o: any) => o.status === "IN_PROGRESS").length ||
            0
          }
          icon={<Clock className="h-6 w-6" />}
          color="sky"
          loading={isLoading}
        />
        <StatCard
          title="Pendientes"
          value={
            operations?.filter((o: any) => o.status === "PENDING").length || 0
          }
          icon={<AlertCircle className="h-6 w-6" />}
          color="amber"
          loading={isLoading}
        />
        <StatCard
          title="Completadas (Hoy)"
          value={
            operations?.filter((o: any) => o.status === "COMPLETED").length || 0
          }
          icon={<CheckCircle2 className="h-6 w-6" />}
          color="emerald"
          loading={isLoading}
        />
      </div>

      <div className="rounded-3xl border border-white/5 bg-slate-900/50 backdrop-blur-xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/5 text-slate-400 text-xs uppercase tracking-wider">
                <th className="px-6 py-4 font-semibold">Referencia</th>
                <th className="px-6 py-4 font-semibold">Cliente</th>
                <th className="px-6 py-4 font-semibold">Estado</th>
                <th className="px-6 py-4 font-semibold">Fecha</th>
                <th className="px-6 py-4 font-semibold text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {operations?.map((op: any) => {
                const statusStyle = STATUS_OPTIONS.find(
                  (s) => s.value === op.status,
                );
                return (
                  <tr
                    key={op.id}
                    className="hover:bg-white/2 transition-colors group"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-xl bg-slate-800 flex items-center justify-center border border-white/5">
                          <Plane className="h-5 w-5 text-sky-400" />
                        </div>
                        <div>
                          <div className="font-medium text-white">
                            {op.title}
                          </div>
                          <div className="text-xs text-slate-500">
                            ID: {String(op.id).padStart(6, "0").toUpperCase()}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-300">
                      {clientMap.get(op.client_id) || "N/A"}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusStyle?.color}`}
                      >
                        {statusStyle?.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-400">
                      {op.created_at ? formatDate(op.created_at) : "-"}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => openModal(op)}
                          className="p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-all"
                        >
                          <Edit2 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => deleteMutation.mutate(op.id)}
                          className="p-2 hover:bg-rose-500/10 rounded-lg text-slate-400 hover:text-rose-400 transition-all"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <AnimatePresence>
        {isModalOpen && (
          <div className="fixed inset-0 z-100 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
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
                <h2 className="text-xl font-bold text-white">
                  {editingOp ? "Actualizar Operación" : "Nueva Operación"}
                </h2>
                <button
                  onClick={closeModal}
                  className="text-slate-400 hover:text-white"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form
                className="space-y-4"
                onSubmit={(e) => {
                  e.preventDefault();
                  saveMutation.mutate(formData);
                }}
              >
                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Título de Operación
                  </label>
                  <input
                    type="text"
                    required
                    className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                    value={formData.title}
                    onChange={(e) =>
                      setFormData({ ...formData, title: e.target.value })
                    }
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Cliente Asignado
                  </label>
                  <select
                    required
                    className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                    value={formData.client_id}
                    onChange={(e) =>
                      setFormData({ ...formData, client_id: e.target.value })
                    }
                  >
                    <option value="">Seleccione un cliente...</option>
                    {clients?.map((c: any) => (
                      <option key={c.id} value={c.id}>
                        {c.nombre_completo}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Estado Actual
                  </label>
                  <select
                    className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                    value={formData.status}
                    onChange={(e) =>
                      setFormData({ ...formData, status: e.target.value })
                    }
                  >
                    {STATUS_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Descripción / Notas
                  </label>
                  <textarea
                    rows={3}
                    className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                  />
                </div>

                <div className="pt-4 flex gap-3">
                  <Button
                    type="button"
                    variant="ghost"
                    className="flex-1"
                    onClick={closeModal}
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    className="flex-1"
                    loading={saveMutation.isPending}
                  >
                    {editingOp ? "Actualizar" : "Registrar"}
                  </Button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
