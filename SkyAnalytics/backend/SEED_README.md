# SkyAnalytics Backend - Documentación de Carga de Datos

## 📊 Script de Seed (seed_data.py)

Este script carga masivamente hasta **10 millones de registros** de pasajeros en PostgreSQL de forma eficiente.

### Características

✅ Genera datos realistas con **Faker** (nombres, emails, direcciones)  
✅ Tarjetas de crédito/débito **válidas con algoritmo de Luhn**  
✅ Inserta con **PostgreSQL COPY FROM** (10-100x más rápido que INSERT)  
✅ Procesa en **lotes de 50,000 registros** (no sobrecarga RAM)  
✅ Muestra **velocidad en tiempo real** y estimaciones  
✅ Soporta **modo test** para validar rápidamente  

### Velocidad Esperada

| Hardware | Velocidad | Tiempo para 10M |
|----------|-----------|-----------------|
| SSD local | ~50K regs/seg | ~3-4 minutos |
| HDD local | ~20K regs/seg | ~8-10 minutos |
| Red lenta | ~5K regs/seg | ~30+ minutos |

### Uso

#### 1️⃣ **Modo Test** (1,000 registros - válida todo funciona)
```bash
cd backend
python seed_data.py --test
```

#### 2️⃣ **Cargar 1 Millón** (prueba rápida)
```bash
python seed_data.py --rows 1000000
```

#### 3️⃣ **Cargar 10 Millones** (carga completa)
```bash
python seed_data.py --rows 10000000
```

#### 4️⃣ **Con truncate** (borra datos anteriores)
```bash
python seed_data.py --rows 1000000 --truncate
```

### Requisitos Previos

1. **Docker corriendo:**
```bash
docker-compose up
```

2. **BD PostgreSQL lista:**
```bash
# Esperar a que en logs aparezca: "database system is ready"
```

3. **Variables de entorno (.env):**
```
DATABASE_URL=postgresql://admin:secretpassword@db:5432/skyanalytics
DB_USER=admin
DB_PASS=secretpassword
DB_HOST=db  # o localhost si corres fuera de Docker
POSTGRES_DB=skyanalytics
```

### Ejemplo Completo

```bash
# 1. Iniciar Docker
docker-compose up -d

# 2. Esperar 10 segundos (BD iniciando)
sleep 10

# 3. Prueba rápida
python seed_data.py --test --truncate

# 4. Cargar 1M de verdad
python seed_data.py --rows 1000000 --truncate

# 5. Después probar API
curl http://localhost:8000/pasajeros?skip=0&limit=10
```

### Validaciones Implementadas

**schemas.py incluye validaciones estrictas:**

✅ **Nombre:** 3-100 caracteres, solo letras/espacios/guiones  
✅ **Email:** Formato válido (EmailStr de Pydantic)  
✅ **Tarjeta Crédito:** Algoritmo de Luhn, 13-19 dígitos  
✅ **Tarjeta Débito:** Algoritmo de Luhn, 13-19 dígitos  
✅ **Dirección:** 5-255 caracteres  
✅ **Ciudad:** 2-100 caracteres, no solo números  
✅ **País:** 2-100 caracteres, no solo números  
✅ **Fecha:** No en el futuro  

### Salida del Script

```
============================================================
SEED DATA - Carga Masiva de Pasajeros
============================================================
Registros a generar: 1,000,000
Base de datos: skyanalytics@db
Chunk size: 50,000
============================================================

============================================================
Batch 1: Generando 50,000 registros...
Progreso: 0 / 1,000,000
Generando 50,000 registros con Faker...
  Generados 10,000 registros...
  Generados 20,000 registros...
  Generados 30,000 registros...
  Generados 40,000 registros...
  Generados 50,000 registros...
✓ 50,000 registros generados en memoria
  Batch 1: 50,000 registros insertados con COPY FROM
  Velocidad: 85,000 registros/segundo

...

============================================================
✓ CARGA COMPLETADA
  Registros insertados: 1,000,000
  Tiempo total: 11.67s
  Velocidad promedio: 85,667 registros/segundo
  Tiempo estimado para 10M: 1.9 minutos
============================================================

Total en BD: 1,000,000 registros
```

### Solución de Problemas

**Error: "database system is ready to accept connections"**
→ Espera 20 segundos para que PostgreSQL inicie completamente

**Error: "UNIQUE constraint failed: pasajeros.correo"**
→ Usa `--truncate` para limpiar datos anteriores

**Error: "connection refused"**
→ Verifica que Docker está corriendo: `docker ps`

**Script muy lento (< 1K registros/seg)**
→ Es normal en HDD. Si está MUCHO más lento, revisa CPU con `top`/`Task Manager`

### Próximos Pasos

1. ✅ Generar datos masivos (`seed_data.py`)
2. ✅ Cargar 1M para testing
3. ✅ Validar que API responde (GET /pasajeros)
4. ✅ Verificar paginación funciona
5. 🔄 Cargar 10M completo (opcional, toma ~3 min en SSD)
6. 🧪 Test de carga API bajo stress

---

## 📋 Endpoints Listos para Probar

```bash
# Listar pasajeros (paginado)
GET http://localhost:8000/pasajeros?skip=0&limit=50

# Obtener perfil (categorización)
GET http://localhost:8000/pasajeros/perfil/1

# Total de pasajeros
GET http://localhost:8000/estadisticas/total-pasajeros

# Por categoría
GET http://localhost:8000/estadisticas/categorias

# Documentación interactiva
GET http://localhost:8000/docs
```

---

## 🔐 Seguridad y Validación

**POR QUÉ validar en Pydantic:**
- Previene inyección SQL (aunque SQLAlchemy ya lo hace)
- Rechaza datos malformados ANTES de BD
- Mantiene integridad de datos
- Valida formato de tarjetas (Luhn checksum)

**Ejemplo de validación:**
```python
# Esto falla - email inválido
POST /pasajeros
{"nombre": "Juan", "correo": "invalido", ...}
→ 422 Validation Error

# Esto falla - tarjeta inválida
POST /pasajeros
{"tarjeta_credito": "1234567890123", ...}
→ 422 Validation Error - Luhn checksum falló

# Esto funciona - todo válido
POST /pasajeros
{"nombre": "Juan", "correo": "juan@email.com", "tarjeta_credito": "4532015112830366", ...}
→ 201 Created
```

---

¡Listo para cargar millones de registros! 🚀
