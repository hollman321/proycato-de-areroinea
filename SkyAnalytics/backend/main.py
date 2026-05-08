import os
from typing import List, Generic, TypeVar
from datetime import date, datetime
from math import ceil

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr

from models import Base, Pasajero, Transaccion, MillasAcumuladas, CategoriaEnum

# TypeVar para schemas genéricos
T = TypeVar('T')

# ==================== CONFIG ====================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:secretpassword@db:5432/skyanalytics"
)

# Crear engine y sesiones
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas
Base.metadata.create_all(bind=engine)

# ==================== FASTAPI APP ====================
app = FastAPI(
    title="SkyAnalytics Backend",
    version="1.0.0",
    description="API para gestionar pasajeros y analytics"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== PYDANTIC SCHEMAS ====================
class PasajeroBase(BaseModel):
    """Schema base para Pasajero (datos comunes)"""
    nombre_completo: str
    correo: EmailStr
    tarjeta_credito: str
    tarjeta_debito: str
    direccion: str
    ciudad: str
    pais: str
    fecha_registro: date


class PasajeroCreate(PasajeroBase):
    """Schema para crear un pasajero"""
    pass


class PasajeroUpdate(BaseModel):
    """Schema para actualizar un pasajero"""
    nombre_completo: str | None = None
    correo: EmailStr | None = None
    tarjeta_credito: str | None = None
    tarjeta_debito: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    pais: str | None = None


class PasajeroResponse(PasajeroBase):
    """Schema para respuestas de pasajero"""
    id: int

    class Config:
        from_attributes = True


# ==================== PAGINACIÓN SCHEMAS ====================
class PaginationMetadata(BaseModel):
    """Metadatos de paginación"""
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    skip: int
    limit: int


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Respuesta genérica paginada.
    
    Contiene:
    - items: lista de resultados
    - pagination: metadatos de paginación
    """
    items: List[T]
    pagination: PaginationMetadata


class PaginatedPasajeros(BaseModel):
    """Respuesta paginada específica para pasajeros"""
    items: List[PasajeroResponse]
    pagination: PaginationMetadata


# ==================== TRANSACCIONES Y MILLAS SCHEMAS ====================

class TransaccionCreate(BaseModel):
    """Schema para crear una transacción"""
    monto: float
    descripcion: str = "Transacción general"


class TransaccionResponse(BaseModel):
    """Schema para respuesta de transacción"""
    id: int
    pasajero_id: int
    monto: float
    millas_ganadas: int
    descripcion: str
    fecha_transaccion: datetime

    class Config:
        from_attributes = True


class MillasResponse(BaseModel):
    """Schema para respuesta de millas acumuladas"""
    pasajero_id: int
    millas_totales: int
    dinero_gastado: float
    fecha_actualizado: datetime

    class Config:
        from_attributes = True


class PerfillPasajero(BaseModel):
    """
    Perfil completo del pasajero con su categorización.
    
    Este es el endpoint de "lógica de negocio" que demuestra
    procesamiento de datos: clasificación automática basada en métricas.
    """
    id: int
    nombre_completo: str
    correo: str
    pais: str
    categoria: str  # PREMIUM, STANDARD, BASICO
    millas_totales: int
    dinero_gastado: float
    numero_transacciones: int
    
    # Beneficios según categoría
    beneficios: List[str]
    
    class Config:
        from_attributes = True


# ==================== DEPENDENCY INJECTION ====================
def get_db():
    """
    Inyección de dependencia para la sesión de base de datos.
    Se abre una conexión para cada request y se cierra al finalizar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== LÓGICA DE NEGOCIO: CATEGORIZACIÓN ====================

# Lista de países "premium" (ofrecen beneficios especiales)
PAISES_PREMIUM = {
    "Estados Unidos", "Canadá", "Reino Unido", "Alemania", "Francia",
    "Japón", "Suiza", "Australia", "Singapur", "Emiratos Árabes"
}

def calcular_categoria(millas_totales: int, dinero_gastado: float, pais: str) -> str:
    """
    Calcula la categoría del pasajero basándose en:
    1. Millas acumuladas
    2. Dinero gastado en transacciones
    3. País de residencia
    
    **Reglas de Categorización:**
    - PREMIUM: > 50,000 millas O > $5,000 gastados O país premium + > 30,000 millas
    - STANDARD: 10,000 - 50,000 millas O $1,000 - $5,000 gastados
    - BASICO: < 10,000 millas O < $1,000 gastados
    """
    # Condición 1: Millas muy altas
    if millas_totales > 50000:
        return CategoriaEnum.PREMIUM
    
    # Condición 2: Mucho dinero gastado
    if dinero_gastado > 5000:
        return CategoriaEnum.PREMIUM
    
    # Condición 3: País premium + buenas millas
    if pais in PAISES_PREMIUM and millas_totales > 30000:
        return CategoriaEnum.PREMIUM
    
    # Condición 4: Standard
    if millas_totales >= 10000 or dinero_gastado >= 1000:
        return CategoriaEnum.STANDARD
    
    # Por defecto: Básico
    return CategoriaEnum.BASICO


def obtener_o_crear_millas(pasajero_id: int, db: Session) -> MillasAcumuladas:
    """Obtiene o crea el registro de millas para un pasajero"""
    millas = db.query(MillasAcumuladas).filter(MillasAcumuladas.pasajero_id == pasajero_id).first()
    if not millas:
        millas = MillasAcumuladas(pasajero_id=pasajero_id, millas_totales=0, dinero_gastado=0)
        db.add(millas)
        db.commit()
    return millas


# ==================== ROUTES ====================

@app.get("/", tags=["Health"])
async def root():
    """Endpoint raíz para verificar que la API está activa"""
    return {
        "message": "Welcome to SkyAnalytics Backend",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health():
    """Endpoint para verificar el estado de la API"""
    return {"status": "healthy"}


# ==================== PASAJEROS ENDPOINTS ====================

@app.post("/pasajeros", response_model=PasajeroResponse, status_code=status.HTTP_201_CREATED, tags=["Pasajeros"])
async def crear_pasajero(
    pasajero: PasajeroCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo pasajero.
    
    La conexión a BD se abre y cierra automáticamente.
    """
    # Verificar que no exista un pasajero con el mismo correo
    db_pasajero = db.query(Pasajero).filter(Pasajero.correo == pasajero.correo).first()
    if db_pasajero:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )

    # Crear nuevo pasajero
    nuevo_pasajero = Pasajero(**pasajero.model_dump())
    db.add(nuevo_pasajero)
    db.commit()
    db.refresh(nuevo_pasajero)
    return nuevo_pasajero


@app.get("/pasajeros", response_model=PaginatedPasajeros, tags=["Pasajeros"])
async def listar_pasajeros(
    skip: int = Query(0, ge=0, description="Registros a saltar (offset)"),
    limit: int = Query(50, ge=1, le=1000, description="Registros por página (max: 1000)"),
    db: Session = Depends(get_db)
):
    """
    Obtener lista paginada de pasajeros.
    
    **Parámetros:**
    - **skip**: registros a saltar (default: 0)
    - **limit**: registros por página, máximo 1000 (default: 50)
    
    **Por qué paginación es vital:**
    - Con 10M de registros, un SELECT * bloquearía la API
    - La paginación carga solo lo necesario en memoria
    - La BD usa índices para hacer OFFSET+LIMIT eficiente
    
    **Ejemplo:**
    - `?skip=0&limit=50` → Primera página (registros 0-49)
    - `?skip=50&limit=50` → Segunda página (registros 50-99)
    - `?skip=100&limit=50` → Tercera página (registros 100-149)
    
    **Respuesta incluye:**
    - items: lista de pasajeros
    - pagination: metadatos (total, página actual, etc.)
    """
    # Obtener el total de registros (eficiente con índice de BD)
    total = db.query(Pasajero).count()
    
    # Validaciones
    if skip < 0:
        skip = 0
    if limit > 1000:
        limit = 1000
    if limit < 1:
        limit = 1
    
    # Calcular paginación
    total_pages = ceil(total / limit) if limit > 0 else 0
    page = (skip // limit) + 1 if limit > 0 else 1
    has_next = skip + limit < total
    has_previous = skip > 0
    
    # Consulta con OFFSET y LIMIT (segura para 10M+ registros)
    pasajeros = (
        db.query(Pasajero)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Metadata de paginación
    pagination = PaginationMetadata(
        total=total,
        page=page,
        page_size=len(pasajeros),
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
        skip=skip,
        limit=limit
    )
    
    return PaginatedPasajeros(
        items=pasajeros,
        pagination=pagination
    )


@app.get("/pasajeros/pagina/{page_number}", response_model=PaginatedPasajeros, tags=["Pasajeros"])
async def obtener_pagina_pasajeros(
    page_number: int = Query(..., ge=1, description="Número de página (comienza en 1)"),
    page_size: int = Query(50, ge=1, le=1000, description="Registros por página (max: 1000)"),
    db: Session = Depends(get_db)
):
    """
    Obtener una página específica de pasajeros.
    
    **Parámetros:**
    - **page_number**: número de página (comienza en 1, no 0)
    - **page_size**: registros por página (default: 50)
    
    **Ejemplo:**
    - `/pagina/1?page_size=50` → Primera página
    - `/pagina/2?page_size=50` → Segunda página
    - `/pagina/3?page_size=50` → Tercera página
    """
    # Convertir número de página a skip
    skip = (page_number - 1) * page_size
    
    # Obtener total
    total = db.query(Pasajero).count()
    
    # Validaciones
    if page_number < 1:
        page_number = 1
    if page_size > 1000:
        page_size = 1000
    
    # Calcular paginación
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    has_next = page_number < total_pages
    has_previous = page_number > 1
    
    # Consulta
    pasajeros = (
        db.query(Pasajero)
        .offset(skip)
        .limit(page_size)
        .all()
    )
    
    pagination = PaginationMetadata(
        total=total,
        page=page_number,
        page_size=len(pasajeros),
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
        skip=skip,
        limit=page_size
    )
    
    return PaginatedPasajeros(
        items=pasajeros,
        pagination=pagination
    )


@app.get("/pasajeros/id/{pasajero_id}", response_model=PasajeroResponse, tags=["Pasajeros"])
async def obtener_pasajero(
    pasajero_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un pasajero específico por su ID.
    """
    pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado"
        )
    return pasajero


@app.put("/pasajeros/id/{pasajero_id}", response_model=PasajeroResponse, tags=["Pasajeros"])
async def actualizar_pasajero(
    pasajero_id: int,
    pasajero_update: PasajeroUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un pasajero existente.
    """
    db_pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not db_pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado"
        )

    # Actualizar solo los campos proporcionados
    actualizar_datos = pasajero_update.model_dump(exclude_unset=True)
    for campo, valor in actualizar_datos.items():
        setattr(db_pasajero, campo, valor)

    db.add(db_pasajero)
    db.commit()
    db.refresh(db_pasajero)
    return db_pasajero


@app.delete("/pasajeros/id/{pasajero_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Pasajeros"])
async def eliminar_pasajero(
    pasajero_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar un pasajero por su ID.
    """
    db_pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not db_pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado"
        )

    db.delete(db_pasajero)
    db.commit()
    return None


@app.get("/pasajeros/buscar/por-correo", response_model=PasajeroResponse, tags=["Pasajeros"])
async def buscar_por_correo(
    correo: str,
    db: Session = Depends(get_db)
):
    """
    Buscar un pasajero por su correo electrónico.
    """
    pasajero = db.query(Pasajero).filter(Pasajero.correo == correo).first()
    if not pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con correo {correo} no encontrado"
        )
    return pasajero


@app.get("/pasajeros/buscar/por-pais", response_model=PaginatedPasajeros, tags=["Pasajeros"])
async def buscar_por_pais(
    pais: str,
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(50, ge=1, le=1000, description="Registros por página"),
    db: Session = Depends(get_db)
):
    """
    Buscar pasajeros por país con paginación.
    
    **Importante:** Esta búsqueda también es paginada para manejar
    casos donde un país tenga millones de registros.
    """
    # Query base
    query = db.query(Pasajero).filter(Pasajero.pais == pais)
    
    # Contar total
    total = query.count()
    
    # Calcular paginación
    total_pages = ceil(total / limit) if limit > 0 else 0
    page = (skip // limit) + 1 if limit > 0 else 1
    has_next = skip + limit < total
    has_previous = skip > 0
    
    # Ejecutar query con paginación
    pasajeros = query.offset(skip).limit(limit).all()
    
    pagination = PaginationMetadata(
        total=total,
        page=page,
        page_size=len(pasajeros),
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
        skip=skip,
        limit=limit
    )
    
    return PaginatedPasajeros(
        items=pasajeros,
        pagination=pagination
    )


# ==================== ESTADÍSTICAS ====================

@app.get("/estadisticas/total-pasajeros", tags=["Estadísticas"])
async def total_pasajeros(db: Session = Depends(get_db)):
    """
    Obtener el total de pasajeros registrados.
    
    **Nota:** Esta operación es O(1) con índice en BD,
    muy rápida incluso con 10M+ registros.
    """
    total = db.query(Pasajero).count()
    return {"total_pasajeros": total}


@app.get("/estadisticas/por-pais", tags=["Estadísticas"])
async def estadisticas_por_pais(db: Session = Depends(get_db)):
    """
    Obtener cantidad de pasajeros agrupados por país.
    
    **Ejemplo de respuesta:**
    ```json
    {
      "estadisticas": [
        {"pais": "Colombia", "cantidad": 250000},
        {"pais": "Mexico", "cantidad": 180000}
      ]
    }
    ```
    """
    from sqlalchemy import func
    
    resultados = (
        db.query(
            Pasajero.pais,
            func.count(Pasajero.id).label('cantidad')
        )
        .group_by(Pasajero.pais)
        .order_by(func.count(Pasajero.id).desc())
        .all()
    )
    
    estadisticas = [
        {"pais": r[0], "cantidad": r[1]} for r in resultados
    ]
    
    return {"estadisticas": estadisticas}


@app.get("/estadisticas/resumen", tags=["Estadísticas"])
async def resumen_estadisticas(db: Session = Depends(get_db)):
    """
    Obtener resumen general de estadísticas.
    
    Información rápida sobre la base de datos.
    """
    from sqlalchemy import func
    
    total = db.query(Pasajero).count()
    paises_unicos = db.query(func.count(func.distinct(Pasajero.pais))).scalar()
    ciudades_unicas = db.query(func.count(func.distinct(Pasajero.ciudad))).scalar()
    
    return {
        "total_pasajeros": total,
        "paises_unicos": paises_unicos,
        "ciudades_unicas": ciudades_unicas,
        "fecha_consulta": date.today()
    }


# ==================== LÓGICA DE NEGOCIO: CATEGORIZACIÓN ====================

def obtener_beneficios(categoria: str) -> List[str]:
    """Retorna la lista de beneficios según la categoría"""
    beneficios_map = {
        CategoriaEnum.PREMIUM: [
            "✈️ Acceso a salas VIP",
            "🎁 Doble acumulación de millas",
            "🅰️ Upgrade prioritario a primera clase",
            "🎫 Tarjeta de embarque prioritario",
            "💼 Asistencia 24/7 dedicada"
        ],
        CategoriaEnum.STANDARD: [
            "✈️ Acceso a salas de espera mejoradas",
            "🎁 Acumulación normal de millas",
            "🅰️ Upgrade según disponibilidad",
            "🎫 Prioridad media en check-in"
        ],
        CategoriaEnum.BASICO: [
            "✈️ Acceso a salas básicas",
            "🎁 Acumulación lenta de millas",
            "🎫 Check-in estándar"
        ]
    }
    return beneficios_map.get(categoria, [])


@app.get("/pasajeros/perfil/{pasajero_id}", response_model=PerfillPasajero, tags=["Lógica de Negocio"])
async def obtener_perfil_pasajero(
    pasajero_id: int,
    db: Session = Depends(get_db)
):
    """
    🎯 **ENDPOINT DE LÓGICA DE NEGOCIO**
    
    Obtiene el perfil completo del pasajero incluyendo su categoría calculada.
    
    **Aquí ocurre la clasificación automática:**
    1. Obtiene millas acumuladas
    2. Obtiene dinero gastado
    3. Aplica reglas de negocio
    4. Asigna categoría (PREMIUM, STANDARD, BASICO)
    5. Retorna beneficios correspondientes
    
    **Reglas de Categorización:**
    - **PREMIUM**: > 50,000 millas O > $5,000 O (país premium + > 30,000 millas)
    - **STANDARD**: 10,000 - 50,000 millas O $1,000 - $5,000
    - **BASICO**: < 10,000 millas O < $1,000
    """
    # Obtener pasajero
    pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado"
        )
    
    # Obtener o crear millas
    millas = obtener_o_crear_millas(pasajero_id, db)
    
    # Contar transacciones
    numero_transacciones = db.query(Transaccion).filter(Transaccion.pasajero_id == pasajero_id).count()
    
    # Calcular categoría (lógica de negocio)
    categoria = calcular_categoria(
        millas.millas_totales,
        millas.dinero_gastado,
        pasajero.pais
    )
    
    # Obtener beneficios
    beneficios = obtener_beneficios(categoria)
    
    return PerfillPasajero(
        id=pasajero.id,
        nombre_completo=pasajero.nombre_completo,
        correo=pasajero.correo,
        pais=pasajero.pais,
        categoria=categoria,
        millas_totales=millas.millas_totales,
        dinero_gastado=millas.dinero_gastado,
        numero_transacciones=numero_transacciones,
        beneficios=beneficios
    )


@app.post("/pasajeros/{pasajero_id}/transacciones", response_model=TransaccionResponse, status_code=status.HTTP_201_CREATED, tags=["Lógica de Negocio"])
async def registrar_transaccion(
    pasajero_id: int,
    transaccion: TransaccionCreate,
    db: Session = Depends(get_db)
):
    """
    Registra una transacción para un pasajero.
    
    **Lógica:**
    1. Valida que el pasajero exista
    2. Calcula millas ganadas (1 milla por cada $2 USD)
    3. Actualiza totales en tabla de millas
    4. Guarda la transacción
    
    **Ejemplo:**
    - Transacción de $200 → 100 millas ganadas
    - Se suma a millas_totales
    - Se suma a dinero_gastado
    - La categoría se recalcula automáticamente en el perfil
    """
    # Validar pasajero
    pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado"
        )
    
    # Calcular millas (1 milla por cada $2 gastados, mínimo 10)
    millas_ganadas = max(10, int(transaccion.monto / 2))
    
    # Crear transacción
    nueva_transaccion = Transaccion(
        pasajero_id=pasajero_id,
        monto=transaccion.monto,
        millas_ganadas=millas_ganadas,
        descripcion=transaccion.descripcion
    )
    db.add(nueva_transaccion)
    db.flush()  # Para obtener el ID
    
    # Obtener o crear millas y actualizar
    millas = obtener_o_crear_millas(pasajero_id, db)
    millas.millas_totales += millas_ganadas
    millas.dinero_gastado += transaccion.monto
    millas.fecha_actualizado = datetime.utcnow()
    
    db.commit()
    db.refresh(nueva_transaccion)
    
    return nueva_transaccion


@app.get("/pasajeros/{pasajero_id}/transacciones", response_model=List[TransaccionResponse], tags=["Lógica de Negocio"])
async def obtener_historial_transacciones(
    pasajero_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de transacciones de un pasajero.
    
    **Incluye:**
    - Monto de la transacción
    - Millas ganadas
    - Descripción
    - Fecha
    """
    # Validar pasajero
    pasajero = db.query(Pasajero).filter(Pasajero.id == pasajero_id).first()
    if not pasajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pasajero con ID {pasajero_id} no encontrado"
        )
    
    transacciones = (
        db.query(Transaccion)
        .filter(Transaccion.pasajero_id == pasajero_id)
        .order_by(Transaccion.fecha_transaccion.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return transacciones


@app.get("/estadisticas/categorias", tags=["Estadísticas"])
async def estadisticas_por_categoria(db: Session = Depends(get_db)):
    """
    Obtiene cantidad de pasajeros por categoría.
    
    **Demostración de procesamiento:**
    Calcula la categoría de cada pasajero y cuenta cuántos hay en cada nivel.
    """
    # Obtener todos los pasajeros con sus millas
    pasajeros_con_millas = (
        db.query(Pasajero, MillasAcumuladas)
        .outerjoin(MillasAcumuladas)
        .all()
    )
    
    # Contar por categoría
    conteo = {
        "PREMIUM": 0,
        "STANDARD": 0,
        "BASICO": 0
    }
    
    for pasajero, millas in pasajeros_con_millas:
        millas_totales = millas.millas_totales if millas else 0
        dinero_gastado = millas.dinero_gastado if millas else 0
        
        categoria = calcular_categoria(millas_totales, dinero_gastado, pasajero.pais)
        conteo[categoria] += 1
    
    return {
        "estadisticas_categorias": conteo,
        "total": sum(conteo.values())
    }


@app.get("/stats/categoria-promedio", tags=["Estadísticas"])
async def categoria_promedio_por_pais(db: Session = Depends(get_db)):
    """
    Análisis de categoría promedio por país.
    
    Útil para marketing y decisiones de negocio.
    """
    # Obtener pasajeros por país
    resultado = (
        db.query(Pasajero.pais)
        .distinct()
        .all()
    )
    
    stats_por_pais = []
    
    for (pais,) in resultado:
        pasajeros_pais = db.query(Pasajero).filter(Pasajero.pais == pais).all()
        
        if not pasajeros_pais:
            continue
        
        conteo_categoria = {
            "PREMIUM": 0,
            "STANDARD": 0,
            "BASICO": 0
        }
        
        for p in pasajeros_pais:
            millas = db.query(MillasAcumuladas).filter(MillasAcumuladas.pasajero_id == p.id).first()
            millas_totales = millas.millas_totales if millas else 0
            dinero_gastado = millas.dinero_gastado if millas else 0
            
            categoria = calcular_categoria(millas_totales, dinero_gastado, p.pais)
            conteo_categoria[categoria] += 1
        
        porcentaje_premium = (conteo_categoria["PREMIUM"] / len(pasajeros_pais)) * 100
        
        stats_por_pais.append({
            "pais": pais,
            "total_pasajeros": len(pasajeros_pais),
            "premium": conteo_categoria["PREMIUM"],
            "standard": conteo_categoria["STANDARD"],
            "basico": conteo_categoria["BASICO"],
            "porcentaje_premium": round(porcentaje_premium, 2)
        })
    
    # Ordenar por porcentaje de premium descendente
    stats_por_pais.sort(key=lambda x: x["porcentaje_premium"], reverse=True)
    
    return {
        "estadisticas_por_pais": stats_por_pais
    }