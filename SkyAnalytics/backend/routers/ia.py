"""
Router para endpoints de Inteligencia Artificial
Proporciona endpoints para el chatbot IA contextual
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from core.config import get_settings
from deps import get_current_user
from models.user import User
from schemas.ia import (
    IAMessageRequest,
    IAMessageResponse,
    IAContextRequest,
    IAContextResponse,
    IAHelpRequest,
    IAGreetingResponse,
    IAHistoryResponse,
    IAConversationMessage,
)
from services.ia_service import ia_service
from database import get_db

router = APIRouter(prefix="/ai", tags=["AI"])
settings = get_settings()


@router.get("/greeting", response_model=IAGreetingResponse)
async def get_greeting(current_user: User = Depends(get_current_user)):
    """
    Obtiene un saludo inicial con sugerencias

    **Respuesta:**
    - greeting: Mensaje de saludo personalizado
    - suggestions: Lista de preguntas sugeridas
    """
    greeting = ia_service.get_greeting()

    suggestions = [
        "¿Cómo crear una operación?",
        "¿Qué son los KPIs?",
        "¿Cómo agregar un cliente?",
        "¿Cómo generar un reporte?",
        "¿Cómo funciona la automatización?",
    ]

    return {"greeting": greeting, "suggestions": suggestions}


@router.post("/chat", response_model=IAMessageResponse)
async def chat(
    request: IAMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint principal para conversar con la IA

    **Parámetros:**
    - message: El mensaje del usuario
    - route: La ruta actual (ej: /dashboard/operaciones)
    - user_id: ID del usuario (obtenido automáticamente)

    **Respuesta:**
    - message: Respuesta de la IA
    - intent: Intención detectada (help, navigate, create, edit, etc.)
    - suggestions: Preguntas relacionadas
    - quick_tips: Tips rápidos para el módulo actual
    - module_info: Información del módulo actual
    """
    try:
        # Registra mensaje del usuario en historial
        ia_service.add_to_history(request.message, is_user=True)

        # Obtiene respuesta del servicio IA
        answer = ia_service.answer_question(request.message, request.route)

        # Detecta intención
        intent = ia_service.detect_intent(request.message)

        # Obtiene tips rápidos
        quick_tips = ia_service.get_quick_tips(request.route)

        # Obtiene información del módulo
        module_summary = ia_service.get_module_summary(request.route)

        # Obtiene sugerencia inteligente
        suggestion = ia_service.get_smart_suggestion(request.route)
        suggestions = [suggestion] if suggestion else []

        # Registra respuesta en historial
        ia_service.add_to_history(answer, is_user=False)

        return {
            "message": answer,
            "intent": intent,
            "suggestions": suggestions,
            "quick_tips": quick_tips,
            "module_info": module_summary,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error en el servicio de IA: {str(e)}"
        )


@router.post("/context", response_model=IAContextResponse)
async def get_context(
    request: IAContextRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene contexto completo del módulo actual

    **Parámetros:**
    - route: La ruta actual del usuario

    **Respuesta:**
    - module: Nombre del módulo
    - description: Descripción del módulo
    - features: Características principales
    - actions: Acciones disponibles
    - tips: Tips útiles
    - contextual_help: Ayuda contextual generada
    """
    try:
        module_info = ia_service.get_module_summary(request.route)
        contextual_help = ia_service.generate_contextual_help(request.route)

        return {
            "module": module_info.get("module", ""),
            "description": module_info.get("description", ""),
            "features": module_info.get("features", []),
            "actions": module_info.get("actions", []),
            "tips": module_info.get("tips", []),
            "contextual_help": contextual_help,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener contexto: {str(e)}"
        )


@router.post("/help", response_model=IAMessageResponse)
async def get_help(
    request: IAHelpRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene ayuda específica para una pregunta

    **Parámetros:**
    - question: La pregunta del usuario
    - route: La ruta actual (opcional)

    **Respuesta:**
    - message: Respuesta detallada
    - intent: Intención detectada
    - suggestions: Preguntas relacionadas
    - quick_tips: Tips relevantes
    """
    try:
        answer = ia_service.answer_question(request.question, request.route)
        intent = ia_service.detect_intent(request.question)
        quick_tips = ia_service.get_quick_tips(request.route)

        return {
            "message": answer,
            "intent": intent,
            "suggestions": [],
            "quick_tips": quick_tips,
            "module_info": None,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ayuda: {str(e)}")


@router.get("/history", response_model=IAHistoryResponse)
async def get_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene historial de conversación

    **Parámetros:**
    - limit: Cantidad máxima de mensajes a retornar (default: 10)

    **Respuesta:**
    - conversation: Lista de mensajes
    - total_messages: Total de mensajes en la sesión
    """
    try:
        history = ia_service.get_history(limit)

        # Convierte el historial al formato de response
        conversation = [
            IAConversationMessage(
                timestamp=datetime.fromisoformat(msg["timestamp"]),
                is_user=msg["is_user"],
                message=msg["message"],
            )
            for msg in history
        ]

        return {
            "conversation": conversation,
            "total_messages": len(ia_service.conversation_history),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener historial: {str(e)}"
        )


@router.post("/clear-history")
async def clear_history(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Limpia el historial de conversación

    **Respuesta:**
    - success: true si se limpió correctamente
    - message: Mensaje de confirmación
    """
    try:
        ia_service.clear_history()
        return {
            "success": True,
            "message": "Historial de conversación limpiado correctamente",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al limpiar historial: {str(e)}"
        )


@router.get("/modules")
async def get_all_modules(current_user: User = Depends(get_current_user)):
    """
    Obtiene información de todos los módulos disponibles

    **Respuesta:**
    - modules: Dict con información de cada módulo
    """
    try:
        modules = {}
        for module_key, module_info in ia_service.SYSTEM_KNOWLEDGE.items():
            modules[module_key] = {
                "title": module_info.get("title"),
                "description": module_info.get("description"),
                "actions_count": len(module_info.get("actions", [])),
                "features_count": len(module_info.get("features", [])),
            }

        return {"modules": modules, "total": len(modules)}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener módulos: {str(e)}"
        )


@router.get("/quick-links/{module}")
async def get_quick_links(module: str, current_user: User = Depends(get_current_user)):
    """
    Obtiene links rápidos para un módulo específico

    **Parámetros:**
    - module: Nombre del módulo (ej: operaciones, clientes)

    **Respuesta:**
    - links: Lista de acciones rápidas disponibles
    """
    try:
        module_info = ia_service.SYSTEM_KNOWLEDGE.get(module, {})

        if not module_info:
            raise HTTPException(
                status_code=404, detail=f"Módulo '{module}' no encontrado"
            )

        links = [
            {"label": action, "icon": "⚡"}
            for action in module_info.get("actions", [])[:5]
        ]

        return {"module": module_info.get("title"), "links": links}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener links rápidos: {str(e)}"
        )
