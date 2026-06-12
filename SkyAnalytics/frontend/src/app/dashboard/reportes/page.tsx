"use client";

import { Button } from "@/components/ui/Card";
import { formatDate } from "@/lib/utils";
import { useToast } from "@/providers/ToastProvider";
import api from "@/services/api";
import { downloadExcel, downloadPDF } from "@/utils/export";
import {
  DollarSign,
  FileDown,
  FileText,
  Plane,
  Table,
  Users,
} from "lucide-react";
import { useState } from "react";

type ReportType = "finance" | "clients" | "operations";
type ReportFormat = "pdf" | "excel";
type ExportCell = string | number;

interface FinanceRecord {
  id: string | number;
  type: string;
  amount: string | number;
  category: string;
  description?: string;
  date: string;
}

interface ClientRecord {
  id: string | number;
  nombre_completo: string;
  correo: string;
  ciudad?: string;
  pais?: string;
  fecha_registro?: string;
}

interface OperationRecord {
  id: string | number;
  title: string;
  client?: { name?: string };
  client_id?: string | number;
  status: string;
  created_at?: string;
}

type ReportRecord = FinanceRecord | ClientRecord | OperationRecord;

const REPORT_TYPES: Array<{
  id: ReportType;
  name: string;
  icon: typeof DollarSign;
  color: string;
  bg: string;
  description: string;
}> = [
  {
    id: "finance",
    name: "Finanzas y Transacciones",
    icon: DollarSign,
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
    description: "Historial de ingresos, egresos y balances mensuales.",
  },
  {
    id: "clients",
    name: "Cartera de Clientes",
    icon: Users,
    color: "text-sky-400",
    bg: "bg-sky-500/10",
    description: "Listado completo de clientes activos, ubicacion y contacto.",
  },
  {
    id: "operations",
    name: "Operaciones Aereas",
    icon: Plane,
    color: "text-violet-400",
    bg: "bg-violet-500/10",
    description: "Seguimiento de vuelos, estados y operadores asignados.",
  },
];

async function fetchReportData(type: ReportType): Promise<ReportRecord[]> {
  if (type === "finance") {
    const response = await api.get("/finance");
    return response.data;
  }

  if (type === "clients") {
    const response = await api.get("/pasajeros", { params: { limit: 100 } });
    return response.data.items || [];
  }

  const response = await api.get("/operations/", { params: { limit: 100 } });
  return response.data.operations || [];
}

function buildExcelData(type: ReportType, data: ReportRecord[]) {
  if (type === "finance") {
    return (data as FinanceRecord[]).map((item) => ({
      ID: item.id,
      Tipo: item.type === "INCOME" ? "Ingreso" : "Gasto",
      Monto: item.amount,
      Categoria: item.category,
      Descripcion: item.description || "",
      Fecha: formatDate(item.date),
    }));
  }

  if (type === "clients") {
    return (data as ClientRecord[]).map((item) => ({
      ID: item.id,
      Nombre: item.nombre_completo,
      Email: item.correo,
      Ciudad: item.ciudad,
      Pais: item.pais,
      Registro: item.fecha_registro ? formatDate(item.fecha_registro) : "-",
    }));
  }

  return (data as OperationRecord[]).map((item) => ({
    ID: item.id,
    Titulo: item.title,
    Cliente: item.client?.name || item.client_id || "N/A",
    Estado: item.status,
    Fecha: item.created_at ? formatDate(item.created_at) : "-",
  }));
}

function buildPdfData(
  type: ReportType,
  data: ReportRecord[],
): { title: string; headers: string[]; rows: ExportCell[][] } {
  if (type === "finance") {
    return {
      title: "Reporte Consolidado de Finanzas",
      headers: ["REF ID", "TIPO", "MONTO", "CATEGORIA", "FECHA"],
      rows: (data as FinanceRecord[]).map((item) => [
        String(item.id).slice(-6).toUpperCase(),
        item.type,
        `$${item.amount}`,
        item.category,
        formatDate(item.date),
      ]),
    };
  }

  if (type === "clients") {
    return {
      title: "Reporte de Base de Datos de Clientes",
      headers: ["NOMBRE", "EMAIL", "CIUDAD", "PAIS"],
      rows: (data as ClientRecord[]).map((item) => [
        item.nombre_completo,
        item.correo,
        item.ciudad || "-",
        item.pais || "-",
      ]),
    };
  }

  return {
    title: "Reporte Operacional de Trafico",
    headers: ["TITULO", "CLIENTE", "ESTADO", "FECHA"],
    rows: (data as OperationRecord[]).map((item) => [
      item.title,
      item.client?.name || item.client_id || "N/A",
      item.status,
      item.created_at ? formatDate(item.created_at) : "-",
    ]),
  };
}

export default function ReportesPage() {
  const [loading, setLoading] = useState<string | null>(null);
  const { success, error, info } = useToast();

  const handleExport = async (type: ReportType, format: ReportFormat) => {
    const loadingKey = `${type}-${format}`;
    setLoading(loadingKey);
    info(`Generando reporte de ${type}...`);

    try {
      const data = await fetchReportData(type);

      if (!data.length) {
        error("No hay datos disponibles para generar el reporte.");
        return;
      }

      if (format === "excel") {
        downloadExcel(buildExcelData(type, data), `reporte_${type}`);
      } else {
        const { title, headers, rows } = buildPdfData(type, data);
        downloadPDF(title, headers, rows, `reporte_${type}`);
      }

      success(`Reporte ${format.toUpperCase()} generado correctamente`);
    } catch {
      error(
        "Error al generar el reporte. Verifique la conexion con el servidor.",
      );
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <div className="h-12 w-12 rounded-2xl bg-sky-500/10 flex items-center justify-center border border-sky-500/20">
          <FileText className="h-6 w-6 text-sky-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-white">Centro de Reportes</h1>
          <p className="text-slate-400 mt-1">
            Exportacion oficial de datos operacionales y financieros.
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {REPORT_TYPES.map((report) => (
          <div
            key={report.id}
            className="rounded-3xl border border-white/5 bg-slate-900/50 p-6 backdrop-blur-xl shadow-2xl transition-all hover:bg-slate-900/80"
          >
            <div
              className={`h-12 w-12 rounded-2xl ${report.bg} flex items-center justify-center mb-4`}
            >
              <report.icon className={`h-6 w-6 ${report.color}`} />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">{report.name}</h3>
            <p className="text-sm text-slate-400 mb-6">{report.description}</p>

            <div className="flex flex-col gap-3">
              <Button
                variant="secondary"
                icon={<Table className="h-4 w-4" />}
                loading={loading === `${report.id}-excel`}
                onClick={() => handleExport(report.id, "excel")}
              >
                Generar Excel (.xlsx)
              </Button>
              <Button
                variant="ghost"
                icon={<FileDown className="h-4 w-4" />}
                loading={loading === `${report.id}-pdf`}
                onClick={() => handleExport(report.id, "pdf")}
              >
                Exportar PDF (.pdf)
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
