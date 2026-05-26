"""
Autenticación: login JWT, registro, perfil y flujo de “olvidé contraseña” (stub).

JWT stateless: el logout es principalmente borrar el token en el cliente.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.security import create_access_token
from database import get_db
from deps import get_current_active_user
from models.user import User
from schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)
from services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        user.email,
        remember_me=request.remember_me,
        extra_claims={"tenant_id": user.tenant_id},
    )
    return TokenResponse(access_token=token)


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if auth_service.get_user_by_email(db, body.email):
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    user = auth_service.create_user(
        db,
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        role="analyst",
    )
    return user


@router.get("/me", response_model=UserPublic)
async def me(user: User = Depends(get_current_active_user)):
    return user


@router.post("/logout")
async def logout():
    """El cliente debe descartar el token; aquí solo confirmamos cierre de sesión lógico."""
    return {"detail": "Sesión cerrada en el cliente"}


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(_: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # No revelamos si el email existe (buena práctica de seguridad).
    # En producción aquí encolarías un email con token de reset.
    _ = db  # reservado para futura lógica (buscar usuario, guardar token, etc.)
    return ForgotPasswordResponse(
        message="Si el correo existe en el sistema, recibirás instrucciones para restablecer la contraseña."
    )
