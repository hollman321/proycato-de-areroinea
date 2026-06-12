"use client";

import { Button } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { useToast } from "@/providers/ToastProvider";
import api from "@/services/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import {
  Building2,
  Edit2,
  Filter,
  Mail,
  Search,
  Trash2,
  UserPlus,
  Users,
  X,
} from "lucide-react";
import { useState } from "react";

interface Client {
  id: number;
  nombre_completo: string;
  correo: string;
  pais: string;
  ciudad: string;
  tarjeta_credito: string;
  tarjeta_debito: string;
  direccion: string;
  fecha_registro: string;
}

interface ClientForm {
  nombre_completo: string;
  correo: string;
  tarjeta_credito: string;
  tarjeta_debito: string;
  direccion: string;
  ciudad: string;
  pais: string;
  fecha_registro: string;
}

interface ClientsSummary {
  total_pasajeros: number;
  nuevos_30d: number;
  regiones: number;
}

export default function ClientesPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [formData, setFormData] = useState<ClientForm>({
    nombre_completo: "",
    correo: "",
    tarjeta_credito: "",
    tarjeta_debito: "",
    direccion: "",
    ciudad: "",
    pais: "",
    fecha_registro: new Date().toISOString().slice(0, 10),
  });

  const queryClient = useQueryClient();
  const { success, error } = useToast();

  // 1. Obtener Clientes
  const { data: clients, isLoading } = useQuery({
    queryKey: ["clients"],
    queryFn: async () => {
      const res = await api.get("/pasajeros", { params: { limit: 50 } });
      return res.data.items;
    },
  });

  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ["clients-summary"],
    queryFn: async () => {
      const res = await api.get<ClientsSummary>(
        "/estadisticas/clientes-resumen",
      );
      return res.data;
    },
    staleTime: 10000,
  });

  // 2. Mutación para Crear/Editar
  const saveMutation = useMutation({
    mutationFn: async (data: ClientForm) => {
      if (editingClient) {
        return api.put(`/pasajeros/${editingClient.id}`, data);
      }
      return api.post("/pasajeros", data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      success(
        editingClient ? "Cliente actualizado" : "Cliente creado con éxito",
      );
      closeModal();
    },
    onError: (err: unknown) => {
      type AxiosErrorLike = {
        response?: { data?: { detail?: string } };
      };

      const isAxiosError = (value: unknown): value is AxiosErrorLike =>
        typeof value === "object" && value !== null && "response" in value;

      const message = isAxiosError(err) ? err.response?.data?.detail : null;
      error(message || "Ocurrió un error al guardar los datos");
    },
  });

  const openModal = (client?: Client) => {
    if (client) {
      setEditingClient(client);
      setFormData({
        nombre_completo: client.nombre_completo,
        correo: client.correo,
        tarjeta_credito: client.tarjeta_credito,
        tarjeta_debito: client.tarjeta_debito,
        direccion: client.direccion,
        ciudad: client.ciudad,
        pais: client.pais,
        fecha_registro:
          client.fecha_registro?.slice(0, 10) ||
          new Date().toISOString().slice(0, 10),
      });
    } else {
      setEditingClient(null);
      setFormData({
        nombre_completo: "",
        correo: "",
        tarjeta_credito: "",
        tarjeta_debito: "",
        direccion: "",
        ciudad: "",
        pais: "",
        fecha_registro: new Date().toISOString().slice(0, 10),
      });
    }
    setIsModalOpen(true);
  };

  const closeModal = () => setIsModalOpen(false);

  // 3. Mutación para Eliminar
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => api.delete(`/pasajeros/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      success("Cliente eliminado correctamente");
    },
    onError: () => error("No se pudo eliminar el cliente"),
  });

  const filteredClients = clients?.filter(
    (c: Client) =>
      c.nombre_completo.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.correo.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="space-y-8 w-full flex flex-col">
      {/* Header & Acciones Rápidas */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Gestión de Clientes</h1>
          <p className="text-slate-400 mt-1">
            Administra la base de datos central de pasajeros y corporativos.
          </p>
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
          value={summary?.total_pasajeros ?? clients?.length ?? 0}
          icon={<Users className="h-6 w-6" />}
          color="sky"
          loading={isLoading || loadingSummary}
        />
        <StatCard
          title="Nuevos (30d)"
          value={summary?.nuevos_30d ?? 0}
          subtitle="Clientes registrados en los últimos 30 días"
          icon={<UserPlus className="h-6 w-6" />}
          color="emerald"
          loading={isLoading || loadingSummary}
        />
        <StatCard
          title="Regiones"
          value={summary?.regiones ?? 0}
          icon={<Building2 className="h-6 w-6" />}
          color="violet"
          loading={isLoading || loadingSummary}
        />
      </div>

      {/* Tabla Enterprise */}
      <div className="rounded-3xl border border-white/5 bg-slate-900/50 backdrop-blur-xl overflow-hidden shadow-2xl">
        <div className="p-6 border-b border-white/5 flex flex-col sm:flex-row gap-4 justify-between items-center">
          <div className="relative w-full sm:max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder="Buscar por nombre o correo..."
              className="w-full bg-slate-950/50 border border-white/10 rounded-xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/50 transition-all"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex gap-2 w-full sm:w-auto">
            <Button
              variant="ghost"
              size="sm"
              icon={<Filter className="h-4 w-4" />}
            >
              Filtros
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() =>
                queryClient.invalidateQueries({ queryKey: ["clients"] })
              }
            >
              Actualizar
            </Button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/5 text-slate-400 text-xs uppercase tracking-wider">
                <th className="px-6 py-4 font-semibold">Cliente</th>
                <th className="px-6 py-4 font-semibold">Contacto</th>
                <th className="px-6 py-4 font-semibold">Ubicación</th>
                <th className="px-6 py-4 font-semibold">Registro</th>
                <th className="px-6 py-4 font-semibold text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {isLoading
                ? [...Array(5)].map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td colSpan={5} className="px-6 py-4">
                        <div className="h-8 bg-white/5 rounded-lg w-full" />
                      </td>
                    </tr>
                  ))
                : filteredClients?.map((client: Client) => (
                    <tr
                      key={client.id}
                      className="hover:bg-white/2 transition-colors group"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-full bg-sky-500/10 flex items-center justify-center text-sky-400 font-bold border border-sky-500/20">
                            {client.nombre_completo.charAt(0)}
                          </div>
                          <div className="font-medium text-white">
                            {client.nombre_completo}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm space-y-1">
                          <div className="flex items-center gap-2 text-slate-300">
                            <Mail className="h-3 w-3" /> {client.correo}
                          </div>
                          <div className="flex items-center gap-2 text-slate-500">
                            <Building2 className="h-3 w-3" /> {client.ciudad},{" "}
                            {client.pais}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-300">
                        {client.direccion || (
                          <span className="text-slate-600">—</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-300">
                        {new Date(client.fecha_registro).toLocaleDateString(
                          "es-ES",
                        )}
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
                  {editingClient ? "Editar Cliente" : "Nuevo Cliente"}
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
                    Nombre Completo
                  </label>
                  <input
                    type="text"
                    required
                    className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                    value={formData.nombre_completo}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        nombre_completo: e.target.value,
                      })
                    }
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Correo Corporativo
                  </label>
                  <input
                    type="email"
                    required
                    className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                    value={formData.correo}
                    onChange={(e) =>
                      setFormData({ ...formData, correo: e.target.value })
                    }
                  />
                </div>
                <div className="grid grid-cols-1 gap-4">
                  <div>
                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      Tarjeta de Crédito
                    </label>
                    <input
                      type="text"
                      required
                      className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                      value={formData.tarjeta_credito}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          tarjeta_credito: e.target.value,
                        })
                      }
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      Tarjeta de Débito
                    </label>
                    <input
                      type="text"
                      required
                      className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                      value={formData.tarjeta_debito}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          tarjeta_debito: e.target.value,
                        })
                      }
                    />
                  </div>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Dirección
                  </label>
                  <input
                    type="text"
                    required
                    className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                    value={formData.direccion}
                    onChange={(e) =>
                      setFormData({ ...formData, direccion: e.target.value })
                    }
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      Ciudad
                    </label>
                    <input
                      type="text"
                      required
                      className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                      value={formData.ciudad}
                      onChange={(e) =>
                        setFormData({ ...formData, ciudad: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                      País
                    </label>
                    <input
                      type="text"
                      required
                      className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                      value={formData.pais}
                      onChange={(e) =>
                        setFormData({ ...formData, pais: e.target.value })
                      }
                    />
                  </div>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Fecha de registro
                  </label>
                  <input
                    type="date"
                    required
                    className="mt-1 w-full rounded-xl bg-slate-950 border border-white/10 p-3 text-sm text-white focus:ring-2 focus:ring-sky-500/50"
                    value={formData.fecha_registro}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        fecha_registro: e.target.value,
                      })
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
                    {editingClient ? "Actualizar" : "Guardar"}
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
