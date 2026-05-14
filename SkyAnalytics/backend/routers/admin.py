"""
Endpoints de administración y monitoreo de la base de datos.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_active_user
from models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/db/tables")
async def get_db_tables(
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Obtener todas las tablas y su estructura"""
    if _.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    inspector = inspect(db.bind)
    tables_info = {}

    for table_name in inspector.get_table_names():
        if table_name == "alembic_version":
            continue

        columns = []
        for col in inspector.get_columns(table_name):
            columns.append(
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "primary_key": col.get("primary_key", False),
                }
            )

        # Contar registros
        result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()

        tables_info[table_name] = {"columnas": columns, "total_registros": count}

    return {"tablas": tables_info}


@router.get("/db/users")
async def get_users_data(
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """Ver todos los usuarios en la base de datos con paginación"""
    if _.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    result = db.execute(text("""
        SELECT id, full_name, email, role, is_active, created_at 
        FROM users
        LIMIT :limit OFFSET :offset
    """).bindparams(limit=limit, offset=offset))

    usuarios = []
    for row in result:
        usuarios.append(
            {
                "id": row[0],
                "full_name": row[1],
                "email": row[2],
                "role": row[3],
                "is_active": row[4],
                "created_at": str(row[5]) if row[5] else None,
            }
        )

    # Contar total
    total_result = db.execute(text("SELECT COUNT(*) FROM users"))
    total = total_result.scalar()

    return {"usuarios": usuarios, "total": total, "limit": limit, "offset": offset}


@router.get("/db/stats")
async def get_db_stats(
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Estadísticas generales de la base de datos"""
    if _.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    stats = {}

    # Pasajeros
    result = db.execute(text("SELECT COUNT(*) FROM pasajeros"))
    stats["pasajeros_total"] = result.scalar()

    # Transacciones
    result = db.execute(text("SELECT COUNT(*) FROM transacciones"))
    stats["transacciones_total"] = result.scalar()

    # Aeropuertos
    result = db.execute(text("SELECT COUNT(*) FROM airports"))
    stats["aeropuertos_total"] = result.scalar()

    # Millas
    result = db.execute(text("SELECT SUM(millas) FROM millas_acumuladas"))
    stats["millas_total"] = result.scalar() or 0

    # Usuarios
    result = db.execute(text("SELECT COUNT(*) FROM users"))
    stats["usuarios_total"] = result.scalar()

    return stats
