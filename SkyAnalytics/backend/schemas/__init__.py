"""
Schemas Pydantic: reexportamos todo para compatibilidad con `from schemas import X`.
"""

from schemas.analytics import CursorPasajerosResponse, MesCantidad, PaisCantidad, ResumenAnalytics
from schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)
from schemas.pagination import PaginatedResponse, PaginationMetadata
from schemas.pasajero import (
    MillasResponse,
    PasajeroCreate,
    PasajeroResponse,
    PasajeroUpdate,
    PasajeroSchemaBase,
    PerfillPasajero,
    TransaccionCreate,
    TransaccionResponse,
    ValidadorTarjeta,
    PaginatedPasajeros,
)

__all__ = [
    "CursorPasajerosResponse",
    "ForgotPasswordRequest",
    "ForgotPasswordResponse",
    "LoginRequest",
    "MesCantidad",
    "MillasResponse",
    "PaginatedPasajeros",
    "PaginatedResponse",
    "PaginationMetadata",
    "PasajeroCreate",
    "PasajeroResponse",
    "PasajeroSchemaBase",
    "PasajeroUpdate",
    "PerfillPasajero",
    "PaisCantidad",
    "RegisterRequest",
    "ResumenAnalytics",
    "TokenResponse",
    "TransaccionCreate",
    "TransaccionResponse",
    "UserPublic",
    "ValidadorTarjeta",
]
