"""CRUD y operaciones de pasajeros (protegidas con JWT)."""

from __future__ import annotations

import logging
from datetime import datetime
from math import ceil
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_active_user
from models.pasajero import MillasAcumuladas, Pasajero, Transaccion
from models.user import User
from schemas.pagination import PaginationMetadata
from schemas.pasajero import (
    PaginatedPasajeros,
    PasajeroCreate,
    PasajeroResponse,
    PasajeroUpdate,
    PerfilPasajero,
    TransaccionCreate,
    TransaccionResponse,
)
from services import analytics_cache, categoria_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Pasajeros"])


@router.post(
    "/pasajeros", response_model=PasajeroResponse, status_code=status.HTTP_201_CREATED
)
async def crear_pasajero(
    pasajero: PasajeroCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    try:
        db_pasajero = (
            db.query(Pasajero).filter(Pasajero.correo == pasajero.correo).first()
        )
        if db_pasajero:
            logger.warning(
                "Intento de crear pasajero con correo duplicado: %s", pasajero.correo
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado",
            )
        nuevo = Pasajero(**pasajero.model_dump())
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        analytics_cache.invalidate_dashboard_cache()
        logger.info("Pasajero creado: %s", nuevo.id)
        return nuevo
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error al crear pasajero: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.get("/pasajeros", response_model=PaginatedPasajeros)
async def listar_pasajeros(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    total = db.query(Pasajero).count()
    if limit > 1000:
        limit = 1000
    if limit < 1:
        limit = 1
    total_pages = ceil(total / limit) if limit > 0 else 0
    page = (skip // limit) + 1 if limit > 0 else 1
    has_next = skip + limit < total
    has_previous = skip > 0
    pasajeros = db.query(Pasajero).offset(skip).limit(limit).all()
    pagination = PaginationMetadata(
        total=total,
        page=page,
        page_size=len(pasajeros),
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
        skip=skip,
        limit=limit,
    )
    return PaginatedPasajeros(items=pasajeros, pagination=pagination)


@router.get("/pasajeros/pagina/{page_number}", response_model=PaginatedPasajeros)
async def obtener_pagina_pasajeros(
    page_number: int = Path(..., ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    skip = (page_number - 1) * page_size
    total = db.query(Pasajero).count()
    if page_size > 1000:
        page_size = 1000
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    has_next = page_number < total_pages
    has_previous = page_number > 1
    pasajeros = db.query(Pasajero).offset(skip).limit(page_size).all()
    pagination = PaginationMetadata(
        total=total,
        page=page_number,
        page_size=len(pasajeros),
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
        skip=skip,
        limit=page_size,
    )
    return PaginatedPasajeros(items=pasajeros, pagination=pagination)


@router.get("/pasajeros/id/{pasajero_id}", response_model=PasajeroResponse)
async def obtener_pasajero(
    pasajero_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado",
        )
    return pasajero


@router.put("/pasajeros/id/{pasajero_id}", response_model=PasajeroResponse)
async def actualizar_pasajero(
    pasajero_id: int,
    pasajero_update: PasajeroUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    db_pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not db_pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado",
        )
    for campo, valor in pasajero_update.model_dump(exclude_unset=True).items():
        setattr(db_pasajero, campo, valor)
    db.add(db_pasajero)
    db.commit()
    db.refresh(db_pasajero)
    analytics_cache.invalidate_dashboard_cache()
    return db_pasajero


@router.delete("/pasajeros/id/{pasajero_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_pasajero(
    pasajero_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    db_pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not db_pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado",
        )
    db.delete(db_pasajero)
    db.commit()
    analytics_cache.invalidate_dashboard_cache()
    return None


@router.get("/pasajeros/buscar/por-correo", response_model=PasajeroResponse)
async def buscar_por_correo(
    correo: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    pasajero = db.query(Pasajero).filter(Pasajero.correo == correo).first()
    if not pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con correo {correo} no encontrado",
        )
    return pasajero


@router.get("/pasajeros/buscar/por-pais", response_model=PaginatedPasajeros)
async def buscar_por_pais(
    pais: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    query = db.query(Pasajero).filter(Pasajero.pais == pais)
    total = query.count()
    total_pages = ceil(total / limit) if limit > 0 else 0
    page = (skip // limit) + 1 if limit > 0 else 1
    has_next = skip + limit < total
    has_previous = skip > 0
    pasajeros = query.offset(skip).limit(limit).all()
    pagination = PaginationMetadata(
        total=total,
        page=page,
        page_size=len(pasajeros),
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
        skip=skip,
        limit=limit,
    )
    return PaginatedPasajeros(items=pasajeros, pagination=pagination)


@router.get("/pasajeros/perfil/{pasajero_id}", response_model=PerfillPasajero)
async def obtener_perfil_pasajero(
    pasajero_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado",
        )
    millas = categoria_service.obtener_o_crear_millas(pasajero_id, db)
    numero_transacciones = (
        db.query(Transaccion).filter(Transaccion.pasajero_id == pasajero_id).count()
    )
    categoria = categoria_service.calcular_categoria(
        millas.millas_totales,
        millas.dinero_gastado,
        pasajero.pais,
        numero_transacciones,
    )
    beneficios = categoria_service.obtener_beneficios(categoria)
    descuento = categoria_service.calcular_nivel_descuento(
        millas.millas_totales,
        millas.dinero_gastado,
        numero_transacciones,
    )
    return PerfilPasajero(
        id=pasajero.id,
        nombre_completo=pasajero.nombre_completo,
        correo=pasajero.correo,
        pais=pasajero.pais,
        categoria=categoria,
        millas_totales=millas.millas_totales,
        dinero_gastado=millas.dinero_gastado,
        numero_transacciones=numero_transacciones,
        beneficios=beneficios,
        descuento=descuento,
    )


@router.post(
    "/pasajeros/{pasajero_id}/transacciones",
    response_model=TransaccionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Lógica de Negocio"],
)
async def registrar_transaccion(
    pasajero_id: int,
    transaccion: TransaccionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado",
        )
    millas_ganadas = max(10, int(transaccion.monto / 2))
    nueva = Transaccion(
        pasajero_id=pasajero_id,
        monto=transaccion.monto,
        millas_ganadas=millas_ganadas,
        descripcion=transaccion.descripcion,
    )
    db.add(nueva)
    db.flush()
    millas = categoria_service.obtener_o_crear_millas(pasajero_id, db)
    millas.millas_totales += millas_ganadas
    millas.dinero_gastado += transaccion.monto
    millas.fecha_actualizado = datetime.utcnow()
    db.commit()
    db.refresh(nueva)
    analytics_cache.invalidate_dashboard_cache()
    return nueva


@router.get(
    "/pasajeros/{pasajero_id}/transacciones",
    response_model=List[TransaccionResponse],
    tags=["Lógica de Negocio"],
)
async def obtener_historial_transacciones(
    pasajero_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado",
        )
    return (
        db.query(Transaccion)
        .filter(Transaccion.pasajero_id == pasajero_id)
        .order_by(Transaccion.fecha_transaccion.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get(
    "/pasajeros/{pasajero_id}", response_model=PasajeroResponse, tags=["Pasajeros"]
)
async def obtener_pasajero_compat(
    pasajero_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    """Compatibilidad con clientes que usan `/pasajeros/{id}` sin el segmento `id/`."""
    pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado",
        )
    return pasajero


@router.put(
    "/pasajeros/{pasajero_id}", response_model=PasajeroResponse, tags=["Pasajeros"]
)
async def actualizar_pasajero_compat(
    pasajero_id: int,
    pasajero_update: PasajeroUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    db_pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not db_pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado",
        )
    for campo, valor in pasajero_update.model_dump(exclude_unset=True).items():
        setattr(db_pasajero, campo, valor)
    db.add(db_pasajero)
    db.commit()
    db.refresh(db_pasajero)
    analytics_cache.invalidate_dashboard_cache()
    return db_pasajero


@router.delete(
    "/pasajeros/{pasajero_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Pasajeros"],
)
async def eliminar_pasajero_compat(
    pasajero_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    db_pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not db_pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado",
        )
    db.delete(db_pasajero)
    db.commit()
    analytics_cache.invalidate_dashboard_cache()
    return None


@router.get(
    "/transacciones/{pasajero_id}",
    response_model=List[TransaccionResponse],
    tags=["Transacciones"],
)
async def obtener_transacciones_compat(
    pasajero_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado",
        )
    return (
        db.query(Transaccion)
        .filter(Transaccion.pasajero_id == pasajero_id)
        .order_by(Transaccion.fecha_transaccion.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
