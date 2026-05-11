# 📐 Arquitectura y Flujo de Datos - SkyAnalytics

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT (Postman/Dashboard)              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    HTTP/JSON (FastAPI)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   FASTAPI BACKEND                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Validación (Pydantic + Luhn)                          │ │
│  │  - Email RFC 5322                                      │ │
│  │  - Tarjetas con Luhn checksum                          │ │
│  │  - Rango de valores                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Inyección de Dependencias (DI)                        │ │
│  │  - get_db() → Session                                  │ │
│  │  - Abre/cierra BD automáticamente                      │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Endpoints                                             │ │
│  │  - CRUD Pasajeros (GET/POST/PUT/DELETE)               │ │
│  │  - Paginación (skip/limit/page_number)                │ │
│  │  - Perfil + Categorización (lógica negocio)           │ │
│  │  - Transacciones (compras/vuelos)                      │ │
│  │  - Estadísticas y reportes                            │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    SQLAlchemy ORM
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              POSTGRESQL DATABASE (10M registros)            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ pasajeros                                              │ │
│  │  - id (PK)                                             │ │
│  │  - nombre_completo                                     │ │
│  │  - correo (UNIQUE)                                     │ │
│  │  - tarjeta_credito, tarjeta_debito                     │ │
│  │  - direccion, ciudad, pais                             │ │
│  │  - fecha_registro                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ transacciones                                          │ │
│  │  - id (PK)                                             │ │
│  │  - pasajero_id (FK) → pasajeros                        │ │
│  │  - monto, millas_ganadas                               │ │
│  │  - descripcion, fecha_transaccion                      │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ millas_acumuladas                                      │ │
│  │  - id (PK)                                             │ │
│  │  - pasajero_id (FK, UNIQUE) → pasajeros               │ │
│  │  - millas_totales, dinero_gastado                      │ │
│  │  - fecha_actualizado                                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Datos: Creación de Pasajero

```
1. CLIENT REQUEST
   POST /pasajeros
   {
     "nombre": "Juan Pérez",
     "correo": "juan@gmail.com",
     "tarjeta_credito": "4532015112830366",
     ...
   }
   │
   ▼
2. PYDANTIC VALIDATION (schemas.py)
   ✓ Email válido (RFC 5322)
   ✓ Tarjeta crédito pasa Luhn
   ✓ Tarjeta débito pasa Luhn
   ✓ Fechas válidas
   │
   ▼
3. DEPENDENCY INJECTION (get_db)
   db = SessionLocal()  ← Abre conexión BD
   │
   ▼
4. VERIFICAR DUPLICADOS
   SELECT * FROM pasajeros WHERE correo = 'juan@gmail.com'
   → No existe ✓
   │
   ▼
5. INSERTAR PASAJERO
   INSERT INTO pasajeros (...)
   VALUES (...)
   RETURNING id, correo, ...
   │
   ▼
6. CREAR REGISTRO DE MILLAS
   INSERT INTO millas_acumuladas (pasajero_id, millas_totales=0)
   │
   ▼
7. COMMIT
   db.commit()
   │
   ▼
8. RESPONSE (201 Created)
   {
     "id": 1,
     "nombre_completo": "Juan Pérez",
     "correo": "juan@gmail.com",
     ...
   }
   │
   ▼
9. CLEANUP (finally)
   db.close()  ← Cierra conexión
```

---

## 📊 Flujo de Datos: Obtener Perfil (Categorización)

```
1. CLIENT REQUEST
   GET /pasajeros/perfil/1
   │
   ▼
2. DEPENDENCY INJECTION
   db = SessionLocal()
   │
   ▼
3. OBTENER PASAJERO
   SELECT * FROM pasajeros WHERE id = 1
   │
   ▼
4. OBTENER MILLAS ACUMULADAS
   SELECT * FROM millas_acumuladas WHERE pasajero_id = 1
   │
   ▼
5. CONTAR TRANSACCIONES
   SELECT COUNT(*) FROM transacciones WHERE pasajero_id = 1
   │
   ▼
6. CALCULAR CATEGORÍA (Lógica de Negocio)
   millas_totales = 75000
   dinero_gastado = $6500
   pais = "Estados Unidos"
   
   IF millas_totales > 50000:
      categoria = "PREMIUM" ✓
   ELSE IF dinero_gastado > $5000:
      categoria = "PREMIUM" ✓
   ELSE IF pais IN paises_premium AND millas > 30000:
      categoria = "PREMIUM" ✓
   ELSE IF millas >= 10000 OR dinero >= $1000:
      categoria = "STANDARD"
   ELSE:
      categoria = "BASICO"
   │
   ▼
7. OBTENER BENEFICIOS
   SWITCH(categoria):
      case "PREMIUM":
         beneficios = [
            "✈️ VIP lounge access",
            "🎁 Double miles",
            "🅰️ Priority upgrade",
            ...
         ]
   │
   ▼
8. RESPONSE (200 OK)
   {
     "id": 1,
     "nombre": "Juan Pérez",
     "categoria": "PREMIUM",
     "millas_totales": 75000,
     "dinero_gastado": 6500,
     "beneficios": ["✈️ VIP...", "🎁 Double..."]
   }
   │
   ▼
9. CLEANUP
   db.close()
```

---

## 🌱 Flujo de Datos: Carga Masiva (seed_data.py)

```
1. LEER CONFIGURACIÓN
   .env → DB_HOST, DB_USER, DB_PASS, POSTGRES_DB
   │
   ▼
2. CONECTAR BD
   psycopg2.connect(...)
   │
   ▼
3. TRUNCAR TABLA (--truncate flag)
   TRUNCATE TABLE pasajeros CASCADE
   │
   ▼
4. LOOP BATCHES (50,000 registros cada uno)
   │
   ├─ BATCH 1 (0-50,000)
   │  │
   │  ├─ GENERAR CON FAKER
   │  │  ├─ Nombre: FAKE.name()
   │  │  ├─ Email: FAKE.email()
   │  │  ├─ Dirección: FAKE.address()
   │  │  ├─ Ciudad: FAKE.city()
   │  │  ├─ País: random.choice(PAISES)
   │  │  ├─ Fecha: FAKE.date_between(-2y, today)
   │  │  └─ Tarjeta: generar_numero_tarjeta() [Luhn válida]
   │  │
   │  ├─ CREAR DATAFRAME (pandas)
   │  │  - 50,000 filas
   │  │  - 8 columnas
   │  │  - Memory: ~30MB
   │  │
   │  └─ INSERTAR CON COPY FROM
   │     ├─ Convertir DataFrame a CSV
   │     ├─ COPY pasajeros FROM STDIN
   │     │  Velocidad: 50K-85K regs/seg
   │     └─ COMMIT
   │
   ├─ BATCH 2 (50,000-100,000)
   │  ...
   │
   └─ BATCH N (hasta 10M)
   │
   ▼
5. MOSTRAR ESTADÍSTICAS
   ├─ Total insertado: 10,000,000
   ├─ Tiempo: 180 segundos
   ├─ Velocidad: 55,556 regs/seg
   └─ Verificar COUNT(*) en BD
   │
   ▼
6. CLEANUP
   conexion.close()
```

---

## 🔐 Validaciones en Capas

```
CLIENTE
   │
   ▼ (HTTP POST)
FASTAPI
   │
   ▼ (Pydantic validation)
SCHEMAS.PY
   ├─ Nombre: regex + length
   ├─ Email: EmailStr (RFC 5322)
   ├─ Tarjeta Crédito: Luhn checksum
   ├─ Tarjeta Débito: Luhn checksum
   └─ Fecha: no > today
   │
   ▼ (pasa validación)
MAIN.PY (Endpoints)
   │
   ▼ (SQL seguro)
SQLALCHEMY ORM
   │ (protege contra inyección SQL)
   ▼
POSTGRESQL
   │
   ▼
BD CONSTRAINTS
   ├─ PRIMARY KEY
   ├─ UNIQUE (correo)
   ├─ NOT NULL
   ├─ FOREIGN KEY
   └─ CHECK constraints
```

---

## ⚡ Optimización de Velocidad

### SIN Optimización
```
INSERT INTO pasajeros (...)
VALUES (...)
INSERT INTO pasajeros (...)
VALUES (...)
... x10,000,000

Velocidad: 100-500 registros/seg
Tiempo: 6-25 horas ❌
```

### CON Optimización (COPY FROM)
```
COPY pasajeros FROM STDIN
│
│ (50,000 registros en 1 segundo)
│
│ (50,000 registros en 1 segundo)
│
│ ... x200 lotes

Velocidad: 50,000-85,000 registros/seg
Tiempo: 3-4 minutos ✅

Ganancia: 100-500x más rápido
```

---

## 📊 Modelo de Datos Completo

```sql
-- PASAJEROS (10M registros)
CREATE TABLE pasajeros (
    id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR NOT NULL,
    correo VARCHAR UNIQUE NOT NULL,
    tarjeta_credito VARCHAR NOT NULL,
    tarjeta_debito VARCHAR NOT NULL,
    direccion VARCHAR NOT NULL,
    ciudad VARCHAR NOT NULL,
    pais VARCHAR NOT NULL,
    fecha_registro DATE NOT NULL
);

-- MILLAS (1:1 con pasajeros)
CREATE TABLE millas_acumuladas (
    id SERIAL PRIMARY KEY,
    pasajero_id INT UNIQUE NOT NULL,
    millas_totales INT DEFAULT 0,
    dinero_gastado FLOAT DEFAULT 0,
    fecha_actualizado DATETIME,
    FOREIGN KEY (pasajero_id) REFERENCES pasajeros(id)
);

-- TRANSACCIONES (N con pasajeros)
CREATE TABLE transacciones (
    id SERIAL PRIMARY KEY,
    pasajero_id INT NOT NULL,
    monto FLOAT NOT NULL,
    millas_ganadas INT DEFAULT 0,
    descripcion VARCHAR,
    fecha_transaccion DATETIME,
    FOREIGN KEY (pasajero_id) REFERENCES pasajeros(id)
);
```

---

## 🎯 Métricas de Rendimiento Esperadas

| Operación | Tiempo | Con 10M registros |
|-----------|--------|------------------|
| GET /pasajeros (skip=0, limit=50) | 50-100ms | Rápido |
| GET /pasajeros/perfil/{id} | 30-50ms | Muy rápido |
| POST /pasajeros (crear) | 100-200ms | Normal |
| GET /estadisticas/total | 10-20ms | Muy rápido |
| Carga masiva (10M registros) | 3-4min | ~55K regs/seg |
| Categorización de 10M | 15-30seg | ~333K regs/seg |

---

¡Sistema escalable, validado y optimizado! 🚀
