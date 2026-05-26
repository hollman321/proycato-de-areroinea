"""
Esquemas (Schemas) para el módulo de Inteligencia Artificial
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class IAMessageRequest(BaseModel):
    """Request para enviar un mensaje al chatbot IA"""

    message: str = Field(
        ..., min_length=1, max_length=1000, description="Mensaje del usuario"
    )
    route: Optional[str] = Field(
        default="", description="Ruta actual del usuario para contexto"
    )
    user_id: Optional[int] = Field(default=None, description="ID del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "¿Cómo crear una nueva operación?",
                "route": "/dashboard/operaciones",
                "user_id": 1,
            }
        }


class IAMessageResponse(BaseModel):
    """Response del chatbot IA"""

    message: str = Field(..., description="Respuesta del asistente IA")
    intent: str = Field(..., description="Intención detectada del mensaje")
    suggestions: Optional[List[str]] = Field(
        default=None, description="Sugerencias relacionadas"
    )
    quick_tips: Optional[List[str]] = Field(default=None, description="Tips rápidos")
    module_info: Optional[dict] = Field(
        default=None, description="Información del módulo actual"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Para crear una nueva operación, haz clic en 'Nueva Operación' en la esquina superior derecha...",
                "intent": "help",
                "suggestions": [
                    "Ver operaciones existentes",
                    "Cambiar estado de operación",
                ],
                "quick_tips": [
                    "Usa los botones de acción en cada fila",
                    "El modal se abre automáticamente",
                ],
            }
        }


class IAContextRequest(BaseModel):
    """Request para obtener contexto del módulo actual"""

    route: str = Field(..., description="Ruta actual del usuario")
    user_id: Optional[int] = Field(default=None, description="ID del usuario")

    class Config:
        json_schema_extra = {"example": {"route": "/dashboard/operaciones"}}


class IAContextResponse(BaseModel):
    """Response con contexto del módulo"""

    module: str = Field(..., description="Nombre del módulo")
    description: str = Field(..., description="Descripción del módulo")
    features: List[str] = Field(..., description="Características principales")
    actions: List[str] = Field(..., description="Acciones disponibles")
    tips: List[str] = Field(..., description="Tips útiles")
    contextual_help: str = Field(..., description="Ayuda contextual generada")

    class Config:
        json_schema_extra = {
            "example": {
                "module": "Centro de Operaciones",
                "description": "Gestión integral de operaciones y procesos",
                "features": ["Tabla de operaciones con CRUD", "Filtrado por estado"],
                "actions": ["Crear nueva operación", "Editar operación"],
                "tips": ["Usa los botones de acción en cada fila"],
                "contextual_help": "Estás en: **Centro de Operaciones**...",
            }
        }


class IAHelpRequest(BaseModel):
    """Request para obtener ayuda específica"""

    question: str = Field(..., min_length=1, description="Pregunta del usuario")
    route: Optional[str] = Field(default="", description="Ruta actual del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "¿Cómo cambiar el estado de una operación?",
                "route": "/dashboard/operaciones",
            }
        }


class IAGreetingResponse(BaseModel):
    """Response con saludo inicial"""

    greeting: str = Field(..., description="Mensaje de saludo")
    suggestions: List[str] = Field(..., description="Preguntas sugeridas")

    class Config:
        json_schema_extra = {
            "example": {
                "greeting": "¡Hola! Soy tu asistente IA de SkyAnalytics. ¿En qué puedo ayudarte?",
                "suggestions": [
                    "¿Cómo crear una operación?",
                    "¿Qué son los KPIs?",
                    "¿Cómo agregar un cliente?",
                ],
            }
        }


class IAConversationMessage(BaseModel):
    """Mensaje individual en el historial de conversación"""

    timestamp: datetime = Field(..., description="Marca de tiempo del mensaje")
    is_user: bool = Field(
        ..., description="True si es del usuario, False si es de la IA"
    )
    message: str = Field(..., description="Contenido del mensaje")
    intent: Optional[str] = Field(
        default=None, description="Intención detectada (solo para IA)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-05-25T19:44:00",
                "is_user": True,
                "message": "¿Cómo crear una nueva operación?",
            }
        }


class IAHistoryResponse(BaseModel):
    """Response con historial de conversación"""

    conversation: List[IAConversationMessage] = Field(
        ..., description="Historial de conversación"
    )
    total_messages: int = Field(..., description="Total de mensajes")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation": [
                    {
                        "timestamp": "2026-05-25T19:44:00",
                        "is_user": True,
                        "message": "¿Hola?",
                    }
                ],
                "total_messages": 1,
            }
        }


class IAQuickLinksResponse(BaseModel):
    """Response con links rápidos por módulo"""

    module: str = Field(..., description="Nombre del módulo")
    links: List[dict] = Field(..., description="Links rápidos")

    class Config:
        json_schema_extra = {
            "example": {
                "module": "Centro de Operaciones",
                "links": [
                    {"label": "Nueva Operación", "action": "create_operation"},
                    {"label": "Ver Operaciones", "action": "view_operations"},
                ],
            }
        }
