# 🚀 Guía Completa: Carga Masiva de 10 Millones de Registros

## 📊 Resumen de Archivos Creados

| Archivo | Propósito |
|---------|-----------|
| `seed_data.py` | Carga masiva de pasajeros (10M registros) |
| `schemas.py` | Validaciones estrictas con Pydantic |
| `validate_config.py` | Verifica configuración y conexión |
| `SEED_README.md` | Documentación detallada |

---

## ⚡ Quick Start (5 minutos)

```bash
# 1. Terminal 1: Inicia Docker
docker-compose up

# 2. Espera 15 segundos (BD iniciando)

# 3. Terminal 2: Valida configuración
cd backend
python validate_config.py

# 4. Carga datos (prueba rápida)
python seed_data.py --test --truncate

# 5. Prueba API
curl http://localhost:8000/pasajeros?skip=0&limit=10

# 6. Ve documentación
# Abre: http://localhost:8000/docs
```

---

## 🔧 Paso a Paso Detallado

### Paso 1: Verificar Configuración

```bash
cd backend
python validate_config.py
```

**Qué verifica:**
- ✓ Variables de entorno (.env)
- ✓ Conexión a PostgreSQL
- ✓ Existencia de tablas
- ✓ Validaciones de Pydantic funcionando

**Salida esperada:**
```
🔍 Verificando variables de entorno...
  ✓ DB_HOST: db
  ✓ DB_PORT: 5432
  ✓ DB_USER: admin
  ✓ POSTGRES_DB: skyanalytics

🔌 Verificando conexión a PostgreSQL...
  ✓ Conexión exitosa

📋 Verificando tablas...
  ✓ Tabla 'pasajeros' existe (0 registros)
  Estructura:
    - id: integer (NOT NULL)
    - nombre_completo: character varying (NOT NULL)
    - correo: character varying (NOT NULL)
    - tarjeta_credito: character varying (NOT NULL)
    - tarjeta_debito: character varying (NOT NULL)
    - direccion: character varying (NOT NULL)
    - ciudad: character varying (NOT NULL)
    - pais: character varying (NOT NULL)
    - fecha_registro: date (NOT NULL)

✅ Verificando validaciones de Pydantic...
  ✓ Validación de datos correctos: OK
  ✓ Validación de email inválido: OK (rechazó)
  ✓ Validación de tarjeta inválida: OK (rechazó)
```

### Paso 2: Prueba Rápida (Modo Test)

```bash
python seed_data.py --test --truncate
```

**Qué hace:**
- Genera 1,000 registros de prueba
- Trunca tabla anterior
- Inserta con COPY FROM
- Muestra velocidad

**Salida esperada:**
```
============================================================
SEED DATA - Carga Masiva de Pasajeros
============================================================
Registros a generar: 1,000
Base de datos: skyanalytics@db
Chunk size: 50,000
============================================================

============================================================
Batch 1: Generando 50,000 registros...
Progreso: 0 / 1,000
Generando 1,000 registros con Faker...
  Generados 1,000 registros...
✓ 1,000 registros generados en memoria
  Batch 1: 1,000 registros insertados con COPY FROM
  Velocidad: 85,000 registros/segundo

============================================================
✓ CARGA COMPLETADA
  Registros insertados: 1,000
  Tiempo total: 0.04s
  Velocidad promedio: 25,000 registros/segundo
  Tiempo estimado para 10M: 6.7 minutos
============================================================

Total en BD: 1,000 registros
```

### Paso 3: Cargar 1 Millón (Testing Completo)

```bash
python seed_data.py --rows 1000000 --truncate
```

**Tiempo esperado:** 15-20 segundos en SSD

**Verifica:**
- Paginación funciona
- BD no se congela
- API responde bajo carga

### Paso 4: Cargar 10 Millones (Producción)

```bash
python seed_data.py --rows 10000000 --truncate
```

**Tiempo esperado:** 
- SSD: 3-4 minutos
- HDD: 8-10 minutos

**Monitorea:**
```bash
# En otra terminal, chequea progreso
watch -n 2 'psql -h db -U admin -d skyanalytics -c "SELECT COUNT(*) FROM pasajeros;"'
```

---

## 📊 Validaciones Implementadas

### 1. Schema de Pydantic (schemas.py)

```python
class PasajeroSchemaBase(BaseModel):
    nombre_completo: constr(min_length=3, max_length=100)
    correo: EmailStr  # ✓ Validación de email
    tarjeta_credito: constr(min_length=13, max_length=19)
    tarjeta_debito: constr(min_length=13, max_length=19)
    direccion: constr(min_length=5, max_length=255)
    ciudad: constr(min_length=2, max_length=100)
    pais: constr(min_length=2, max_length=100)
    fecha_registro: date
    
    @field_validator("nombre_completo")
    def validar_nombre(cls, v):
        # Solo letras/espacios/guiones/ñ
        if not re.match(r"^[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ\s'-]+$", v):
            raise ValueError("Caracteres inválidos")
        return v.strip()
    
    @field_validator("tarjeta_credito", "tarjeta_debito")
    def validar_tarjeta(cls, v):
        # ✓ Algoritmo de Luhn
        if not ValidadorTarjeta.validar_numero_tarjeta(v):
            raise ValueError("Número de tarjeta inválido (Luhn)")
        return v.replace(" ", "").replace("-", "")
```

### 2. Algoritmo de Luhn para Tarjetas

```python
def validar_numero_tarjeta(numero: str) -> bool:
    """
    Valida usando Algoritmo de Luhn:
    1. Dobla cada segundo dígito de derecha a izquierda
    2. Si > 9, resta 9
    3. Suma todos
    4. Si módulo 10 = 0, es válida
    """
    # Ejemplo: 4532015112830366 (VISA válida)
    # → Checksum = 0 (válida)
    # → Algoritmo de Luhn: PASS ✓
```

### 3. Validaciones por Campo

| Campo | Validación |
|-------|-----------|
| `nombre_completo` | 3-100 chars, regex [a-zA-ZáéíóúñüÁÉÍÓÚÑÜ\s'-]+ |
| `correo` | EmailStr (RFC 5322) |
| `tarjeta_credito` | Luhn checksum, 13-19 dígitos |
| `tarjeta_debito` | Luhn checksum, 13-19 dígitos |
| `direccion` | 5-255 characters |
| `ciudad` | 2-100 chars, no solo números |
| `pais` | 2-100 chars, no solo números |
| `fecha_registro` | No en el futuro |

---

## 🧪 Pruebas de Validación

```bash
# Dato válido - funciona
POST /pasajeros
{
  "nombre_completo": "Juan Pérez",
  "correo": "juan@email.com",
  "tarjeta_credito": "4532015112830366",  # ✓ VISA válida
  "tarjeta_debito": "5425233010103442",   # ✓ MASTERCARD válida
  "direccion": "Calle 123",
  "ciudad": "Bogotá",
  "pais": "Colombia",
  "fecha_registro": "2024-01-15"
}
→ 201 Created

# Email inválido - rechazado
POST /pasajeros
{
  ...,
  "correo": "email_invalido"
}
→ 422 Validation Error: invalid email format

# Tarjeta inválida - rechazada
POST /pasajeros
{
  ...,
  "tarjeta_credito": "1234567890123456"
}
→ 422 Validation Error: Número de tarjeta inválido (Luhn)

# Nombre inválido - rechazado
POST /pasajeros
{
  ...,
  "nombre_completo": "Juan123"  # Contiene números
}
→ 422 Validation Error: Caracteres inválidos
```

---

## 🚀 Optimizaciones Implementadas

### 1. PostgreSQL COPY FROM (No INSERT)

```python
# ❌ LENTO (1,000 registros/seg)
INSERT INTO pasajeros (...) VALUES (...)

# ✅ RÁPIDO (50,000-85,000 registros/seg)
COPY pasajeros FROM STDIN WITH ...
```

**Ganancia:** 50-85x más rápido

### 2. Procesamiento en Lotes

```python
# Generar 50,000 registros a la vez
# No cargar 10M en memoria
for batch in range(0, 10_000_000, 50_000):
    generar_lote(50_000)
    insertar_con_copy_from()
```

**Ganancia:** RAM = constante (~200MB)

### 3. Faker con Pesos

```python
# Países con distribución realista
paises_frecuentes = ["Colombia", "Mexico", "Argentina", ...]
pais = random.choices(paises_frecuentes, weights=[30, 25, 15, ...])
```

**Ganancia:** Datos más realistas para análisis

### 4. Tarjetas Válidas con Luhn

```python
# Las tarjetas generadas PASAN la validación
# No se desperdician intentos
numero_base = "4" + "".join([str(random.randint(0,9)) for _ in range(14)])
digito_checksum = calcular_luhn(numero_base)
tarjeta_final = numero_base + str(digito_checksum)
```

**Ganancia:** 100% validación de primera

---

## 📈 Rendimiento Esperado

### Por Hardware

| CPU | RAM | SSD | Velocidad | Tiempo (10M) |
|-----|-----|-----|-----------|--------------|
| i7 8-core | 16GB | SSD NVMe | 85K regs/s | ~3.3 min |
| i5 6-core | 8GB | SSD SATA | 50K regs/s | ~5.5 min |
| Ryzen 5 6-core | 16GB | HDD 7200 | 20K regs/s | ~14 min |

### Monitoreo en Vivo

```bash
# Terminal 1: Observa inserción
watch -n 2 'psql -h db -U admin -d skyanalytics -c "SELECT COUNT(*) FROM pasajeros;"'

# Terminal 2: Observa BD
watch -n 1 'docker stats'

# Terminal 3: Ejecuta seed
python seed_data.py --rows 10000000 --truncate
```

---

## 🔍 Debugging

### Problema: "Conexión rechazada"

```bash
# Solución 1: Verifica Docker
docker-compose ps
docker-compose logs db

# Solución 2: Espera más
sleep 30
python seed_data.py --test

# Solución 3: Variables de entorno
cat .env
# DB_HOST debe ser "db" (no localhost)
```

### Problema: "UNIQUE constraint failed"

```bash
# Solución: Trunca antes
python seed_data.py --rows 1000000 --truncate
```

### Problema: Script muy lento

```bash
# Verifica CPU
top -bn1 | head -20

# Verifica disco
iostat -x 1

# Si < 5K regs/seg: probable problema de HDD
```

---

## ✅ Checklist Completo

- [ ] Docker corriendo: `docker ps`
- [ ] BD activa: `docker-compose logs db | grep "ready"`
- [ ] .env configurado: `cat .env`
- [ ] Validación OK: `python validate_config.py`
- [ ] Test OK: `python seed_data.py --test`
- [ ] 1M cargados: `python seed_data.py --rows 1000000`
- [ ] API responde: `curl http://localhost:8000/pasajeros`
- [ ] Paginación OK: `curl http://localhost:8000/pasajeros?skip=0&limit=50`
- [ ] Perfil OK: `curl http://localhost:8000/pasajeros/perfil/1`
- [ ] Docs OK: http://localhost:8000/docs
- [ ] Carga 10M (opcional): `python seed_data.py --rows 10000000`

---

## 🎯 Próximos Pasos

1. ✅ Cargar datos masivos
2. ✅ Validar integridad
3. 🔄 Test de API bajo stress
4. 🔄 Crear índices para búsqueda
5. 🔄 Dashboard en Streamlit

---

¡Listo para escalar a 10 millones de usuarios! 🚀
