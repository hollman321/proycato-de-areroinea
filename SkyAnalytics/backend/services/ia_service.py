"""
Servicio de IA - Asistente inteligente para SkyAnalytics
Proporciona respuestas contextuales basadas en la ruta actual del usuario
"""

from typing import Optional, Dict, List, Any
import json
from datetime import datetime
import random
import re
import unicodedata


class IAService:
    """Servicio de asistente IA con conocimiento del sistema completo"""

    # Base de conocimiento del sistema
    SYSTEM_KNOWLEDGE = {
        "dashboard": {
            "title": "Panel Ejecutivo",
            "description": "Vista principal con KPIs en tiempo real",
            "features": [
                "Revenue Total - Ingresos totales del período",
                "Operaciones Activas - Cantidad de operaciones en progreso",
                "Total Clientes - Número de clientes registrados",
                "Gráficas de tendencias - Análisis visual de datos",
                "Indicadores de crecimiento - Métricas de desempeño",
            ],
            "actions": [
                "Ver detalles de KPIs",
                "Navegar a módulos específicos",
                "Exportar datos",
                "Actualizar gráficas",
            ],
            "tips": [
                "Los KPIs se actualizan en tiempo real",
                "Haz clic en cualquier métrica para más detalles",
                "Las gráficas muestran tendencias históricas",
                "Puedes exportar los datos a PDF o Excel",
            ],
        },
        "ejecutivo": {
            "title": "Panel Ejecutivo Avanzado",
            "description": "Análisis profundo de métricas de negocio",
            "features": [
                "Resumen ejecutivo",
                "Análisis de rendimiento",
                "Proyecciones financieras",
                "Comparativas periodo vs periodo",
                "Alertas inteligentes",
            ],
            "actions": [
                "Analizar tendencias",
                "Generar reportes",
                "Establecer metas",
                "Comparar periodos",
            ],
            "tips": [
                "Usa las comparativas para identificar patrones",
                "Las proyecciones se basan en datos históricos",
                "Las alertas se activan cuando hay anomalías",
                "Exporta los análisis para presentaciones",
            ],
        },
        "operaciones": {
            "title": "Centro de Operaciones",
            "description": "Gestión integral de operaciones y procesos",
            "features": [
                "Tabla de operaciones con CRUD completo",
                "Filtrado por estado (Pendiente, En Progreso, Completado, Cancelado)",
                "Búsqueda por cliente o referencia",
                "Edición en línea",
                "Eliminación con confirmación",
            ],
            "actions": [
                "Crear nueva operación",
                "Editar operación existente",
                "Cambiar estado de operación",
                "Eliminar operación",
                "Buscar/filtrar operaciones",
            ],
            "tips": [
                "Usa los botones de acción en cada fila",
                "El modal se abre automáticamente al crear/editar",
                "Selecciona el cliente correcto antes de guardar",
                "Los estados se actualizan en tiempo real",
                "Puedes cancelar operaciones desde el menú",
            ],
        },
        "clientes": {
            "title": "Gestión de Clientes",
            "description": "Administración de todos los clientes y contactos",
            "features": [
                "Listado completo de clientes",
                "Información de contacto",
                "Datos de tarjetas (crédito y débito)",
                "Direcciones y ubicación",
                "Histórico de operaciones por cliente",
            ],
            "actions": [
                "Crear nuevo cliente",
                "Editar datos del cliente",
                "Ver detalle del cliente",
                "Eliminar cliente",
                "Buscar cliente por nombre/email",
            ],
            "tips": [
                "Todos los campos son obligatorios",
                "Los datos de tarjeta se almacenan de forma segura",
                "Puedes filtrar por ciudad o país",
                "El histórico muestra todas las operaciones del cliente",
                "Los cambios se guardan automáticamente",
            ],
        },
        "finanzas": {
            "title": "Módulo de Finanzas",
            "description": "Control y análisis de flujos financieros",
            "features": [
                "Dashboard de ingresos y gastos",
                "Análisis de rentabilidad",
                "Proyecciones de flujo de caja",
                "Reportes financieros",
                "Auditoría de transacciones",
            ],
            "actions": [
                "Ver balance actual",
                "Generar reportes",
                "Analizar tendencias",
                "Exportar estados financieros",
            ],
            "tips": [
                "Los ingresos incluyen todas las operaciones completadas",
                "Los gastos se registran automáticamente",
                "Las proyecciones ayudan a la planificación",
                "Revisa los reportes mensualmente",
            ],
        },
        "reportes": {
            "title": "Generador de Reportes",
            "description": "Creación y exportación de reportes personalizados",
            "features": [
                "Reportes por fecha",
                "Reportes por cliente",
                "Reportes por operación",
                "Exportación a PDF",
                "Exportación a Excel",
            ],
            "actions": [
                "Crear reporte",
                "Filtrar datos",
                "Exportar PDF",
                "Exportar Excel",
                "Guardar plantilla",
            ],
            "tips": [
                "Selecciona el rango de fechas primero",
                "Los reportes se generan en segundos",
                "Los PDFs incluyen firma digital",
                "Los Excel son editables",
            ],
        },
        "automatizacion": {
            "title": "Automatización de Procesos",
            "description": "Configuración de flujos automáticos y automatizaciones",
            "features": [
                "Reglas de automatización",
                "Flujos de trabajo",
                "Notificaciones automáticas",
                "Programación de tareas",
                "Integraciones",
            ],
            "actions": [
                "Crear regla de automatización",
                "Configurar flujo de trabajo",
                "Activar/desactivar automatización",
                "Ver historial de ejecuciones",
            ],
            "tips": [
                "Las automatizaciones se ejecutan en tiempo real",
                "Puedes establecer condiciones complejas",
                "Las notificaciones se envían por email",
                "Los flujos se pueden pausar en cualquier momento",
            ],
        },
        "administracion": {
            "title": "Administración del Sistema",
            "description": "Gestión de usuarios, roles y configuración",
            "features": [
                "Gestión de usuarios",
                "Asignación de roles",
                "Control de permisos",
                "Configuración de niveles de acceso",
                "Auditoría de acceso",
            ],
            "actions": [
                "Crear usuario",
                "Asignar roles",
                "Cambiar permisos",
                "Desactivar usuario",
                "Ver registro de acceso",
            ],
            "tips": [
                "Siempre asigna un rol a los usuarios",
                "Revisa los permisos regularmente",
                "Desactiva usuarios inactivos",
                "El registro de acceso muestra toda la actividad",
            ],
        },
        "configuracion": {
            "title": "Configuración del Sistema",
            "description": "Ajustes generales y preferencias del sistema",
            "features": [
                "Tema de color",
                "Idioma",
                "Zona horaria",
                "Notificaciones",
                "Integraciones",
            ],
            "actions": [
                "Cambiar tema",
                "Seleccionar idioma",
                "Configurar notificaciones",
                "Integrar servicios externos",
            ],
            "tips": [
                "Los cambios se aplican inmediatamente",
                "Guarda tus preferencias",
                "Las integraciones mejoran la funcionalidad",
                "Revisa la sección de API para desarrolladores",
            ],
        },
    }

    # Preguntas frecuentes y respuestas por módulo
    COMMON_QUESTIONS = {
        "general": {
            "¿cómo empiezo?": "Bienvenido a SkyAnalytics. Puedes comenzar por el Panel Ejecutivo para ver un resumen de tu negocio. Luego navega a Operaciones para gestionar tus procesos.",
            "¿cómo logearme?": "Usa tus credenciales de acceso. Si olvidaste tu contraseña, haz clic en 'Olvidé mi contraseña' en la pantalla de login.",
            "¿quién puede ayudarme?": "Yo soy tu asistente IA. Puedo resolver dudas sobre cualquier módulo, guiarte en procesos y ayudarte a maximizar SkyAnalytics.",
            "¿qué es skyanalytics?": "SkyAnalytics es una plataforma de inteligencia operacional que te ayuda a gestionar operaciones, clientes y finanzas de tu negocio.",
        },
        "operaciones": {
            "¿cómo crear una operación?": "Haz clic en 'Nueva Operación' en la esquina superior derecha. Completa el formulario con los datos de la operación y selecciona un cliente. Luego haz clic en 'Guardar'.",
            "¿cómo cambiar el estado?": "En la tabla de operaciones, haz clic en el botón de editar (lápiz) en la fila correspondiente. Cambias el estado en el modal y guardas los cambios.",
            "¿cómo eliminar una operación?": "Haz clic en el botón de eliminar (papelera) en la fila de la operación. Se te pedirá confirmación antes de eliminar.",
            "¿cómo buscar operaciones?": "Usa la barra de búsqueda en la parte superior para filtrar por referencia o cliente. También puedes filtrar por estado.",
        },
        "clientes": {
            "¿cómo agregar un cliente?": "Ve a Clientes y haz clic en 'Nuevo Cliente'. Completa todos los campos requeridos: nombre, email, datos de tarjeta, dirección. Haz clic en 'Guardar'.",
            "¿qué datos debo ingresar?": "Necesitas: nombre completo, email, número de tarjeta de crédito, número de tarjeta de débito, dirección, ciudad y país.",
            "¿puedo editar un cliente?": "Sí, haz clic en el botón de editar (lápiz) en la fila del cliente y modifica los datos que necesites.",
            "¿cómo ver el histórico del cliente?": "Haz clic en el nombre del cliente para ver todos sus datos y el histórico de operaciones.",
        },
        "finanzas": {
            "¿cómo ver mis ingresos?": "Ve a Finanzas para ver un dashboard completo con ingresos, gastos y rentabilidad en tiempo real.",
            "¿cómo generar un reporte financiero?": "En Reportes, selecciona el tipo 'Financiero', elige el rango de fechas y haz clic en 'Generar'. Puedes exportar a PDF o Excel.",
            "¿qué incluye el balance?": "El balance incluye todos los ingresos de operaciones completadas, gastos registrados y utilidad neta.",
        },
        "reportes": {
            "¿cómo exportar datos?": "Ve a Reportes, configura los filtros que necesites, genera el reporte y usa los botones 'Exportar PDF' o 'Exportar Excel'.",
            "¿qué formatos están disponibles?": "Puedes exportar a PDF (para visualización y impresión) o Excel (para análisis adicional).",
        },
    }

    # Frases motivacionales según hora
    MOTIVATIONAL_PHRASES = [
        "¡Hola! ¿En qué puedo ayudarte hoy?",
        "Estoy aquí para resolver tus dudas sobre SkyAnalytics.",
        "¿Tienes alguna pregunta sobre el sistema?",
        "Soy tu asistente IA. ¿Necesitas ayuda?",
        "¡Bienvenido! Dime cómo puedo ayudarte.",
    ]

    def __init__(self):
        self.conversation_history: List[Dict] = []

    def _resolve_module_key(self, route: str) -> str:
        """Resuelve el identificador del módulo de forma robusta a partir de la ruta"""
        segments = [s.lower() for s in route.strip("/").split("/") if s]

        # Mapeo de rutas URL a claves de conocimiento del sistema
        path_map = {
            "pasajeros": "clientes",
            "admin": "administracion",
            "enterprise": "ejecutivo",
            "analytics": "dashboard",
            "overview": "ejecutivo",
            "finanzas": "finanzas",
        }

        for segment in reversed(segments):
            if segment in self.SYSTEM_KNOWLEDGE:
                return segment
            if segment in path_map:
                return path_map[segment]

        return "dashboard"

    def get_context_by_route(self, route: str) -> Dict:
        """Obtiene contexto basado en la ruta actual"""
        module_key = self._resolve_module_key(route)
        return self.SYSTEM_KNOWLEDGE[module_key]

    def generate_contextual_help(self, route: str) -> str:
        """Genera ayuda contextual basada en la ruta"""
        module_key = self._resolve_module_key(route)
        context = self.SYSTEM_KNOWLEDGE[module_key]

        help_text = f"Estás en: **{context['title']}**\n\n"
        help_text += f"{context['description']}\n\n"
        help_text += "**¿Qué puedes hacer aquí?**\n"
        for action in context["actions"][:3]:
            help_text += f"• {action}\n"

        return help_text

    def get_quick_tips(self, route: str) -> List[str]:
        """Obtiene tips rápidos para el módulo actual"""
        context = self.get_context_by_route(route)
        if context and "tips" in context:
            return context["tips"][:3]
        return []

    def answer_question(self, question: str, route: str = "") -> str:
        """
        Responde preguntas del usuario de forma flexible.
        Limpia acentos, puntuación y espacios para mejorar el matching.
        """

        def normalize(text: str) -> str:
            # Pasa a minúsculas, quita acentos y puntuación
            text = text.lower().strip()
            text = "".join(
                c
                for c in unicodedata.normalize("NFD", text)
                if unicodedata.category(c) != "Mn"
            )
            return re.sub(r"[¿?¡!.,]", "", text)

        q_clean = normalize(question)
        if not q_clean:
            return "¿En qué puedo ayudarte? Dime qué módulo quieres explorar."

        # Busca en preguntas generales
        for key, answer in self.COMMON_QUESTIONS.get("general", {}).items():
            key_clean = normalize(key)
            if key_clean in q_clean or q_clean in key_clean:
                return answer

        # Busca en el módulo actual
        if route:
            module_key = self._resolve_module_key(route)
            module_questions = self.COMMON_QUESTIONS.get(module_key, {})
            for key, answer in module_questions.items():
                key_clean = normalize(key)
                if key_clean in q_clean or q_clean in key_clean:
                    return answer

        # Si no encuentra, retorna ayuda contextual
        if route:
            return self.generate_contextual_help(route)

        return "No encontré una respuesta específica. ¿Puedes reformular tu pregunta o preguntarme sobre un módulo específico?"

    def get_module_summary(self, route: str) -> Dict:
        """Obtiene resumen completo del módulo"""
        context = self.get_context_by_route(route)
        return {
            "module": context.get("title", "Unknown"),
            "description": context.get("description", ""),
            "features": context.get("features", []),
            "actions": context.get("actions", []),
            "tips": context.get("tips", []),
        }

    def get_greeting(self) -> str:
        """Obtiene un saludo aleatorio"""
        return random.choice(self.MOTIVATIONAL_PHRASES)

    def add_to_history(self, message: str, is_user: bool = True):
        """Agrega mensaje al historial de conversación"""
        self.conversation_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "is_user": is_user,
                "message": message,
            }
        )

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Obtiene historial de conversación"""
        return self.conversation_history[-limit:]

    def clear_history(self):
        """Limpia historial de conversación"""
        self.conversation_history = []

    def detect_intent(self, message: str) -> str:
        """Detecta la intención del usuario"""
        message_lower = message.lower()

        intents = {
            "help": ["ayuda", "help", "cómo", "como", "duda", "no entiendo"],
            "navigate": ["ir a", "voy a", "quiero ir", "abre", "acceso"],
            "create": ["crear", "agregar", "nuevo", "nueva", "add", "new"],
            "edit": ["editar", "modificar", "cambiar", "update"],
            "delete": ["eliminar", "borrar", "quitar", "delete"],
            "export": ["exportar", "descargar", "pdf", "excel", "report"],
            "search": ["buscar", "find", "dónde", "donde", "cuál", "cual"],
        }

        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return "general"

    def get_smart_suggestion(self, route: str, action: str = "") -> str:
        """Proporciona sugerencia inteligente"""
        module_key = self._resolve_module_key(route)
        module = self.SYSTEM_KNOWLEDGE[module_key]

        suggestions = {
            "operaciones": "💡 **Sugerencia:** Revisa regularmente el estado de tus operaciones. Los cambios se actualizan en tiempo real.",
            "clientes": "💡 **Sugerencia:** Mantén los datos de tus clientes actualizados para mejores análisis.",
            "finanzas": "💡 **Sugerencia:** Revisa tu balance diariamente para tomar decisiones informadas.",
            "reportes": "💡 **Sugerencia:** Genera reportes semanales para monitorear el desempeño.",
            "dashboard": "💡 **Sugerencia:** Los KPIs se actualizan automáticamente. Explora los otros módulos para más detalle.",
        }

        return suggestions.get(module_key, "")


# Instancia global del servicio
ia_service = IAService()
