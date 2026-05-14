# SkyAnalytics Operational Intelligence

Plataforma SaaS empresarial de análisis operacional para aerolíneas. Gestiona perfiles de pasajeros (10M+ registros), transacciones, millas acumuladas y proporciona dashboards interactivos en tiempo real.

## Arquitectura

- **Frontend**: Next.js 15 con TypeScript, TailwindCSS, Framer Motion
- **Backend**: API REST con FastAPI, PostgreSQL y SQLAlchemy
- **Dashboard Legacy**: Interfaz de visualización con Streamlit (opcional)
- **Base de Datos**: PostgreSQL con índices optimizados y Redis para caché
- **Contenerización**: Docker multi-servicio con docker-compose
- **DevOps**: Rate limiting, health checks, monitoring básico

## Stack Tecnológico

### Frontend
- Next.js 15 (App Router)
- TypeScript
- TailwindCSS
- Framer Motion (animaciones)
- Recharts (gráficas)
- Zustand (state management)
- React Query (data fetching)
- Axios (HTTP client)

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Redis (caché distribuido)
- JWT Authentication
- SlowAPI (rate limiting)
- Pydantic (validación)

### DevOps
- Docker & Docker Compose
- Alembic (migrations)
- pgAdmin (DB admin)
- Health checks automáticos

## Instalación y Configuración

### Prerrequisitos
- Docker y Docker Compose instalados
- Puertos disponibles: 3000 (Frontend), 8000 (Backend), 5432 (DB), 6379 (Redis), 5050 (pgAdmin)

### Pasos de Instalación

1. **Clonar el repositorio** (o descomprimir el proyecto)
2. **Variables de entorno**: El archivo `.env` ya está configurado para desarrollo local
3. **Levantar los servicios**:
   ```bash
   docker-compose up --build
   ```
   Los contenedores ejecutan automáticamente migraciones, seed de admin y levantan los servicios.

4. **Acceder a los servicios**:
   - **Frontend**: http://localhost:3000 (Next.js app)
   - **API**: http://localhost:8000/docs (Swagger)
   - **Dashboard Legacy**: http://localhost:8501 (opcional, ejecutar con `docker-compose --profile legacy up`)
   - **pgAdmin**: http://localhost:5050 (admin@skyanalytics.com / admin123)

5. **Login demo**: `admin@skyanalytics.com` / `admin123`

## Características Principales

### 🔐 Autenticación y Autorización
- Login/Register con JWT
- Roles: Admin, Supervisor, Cliente
- Protección de rutas
- Refresh tokens
- Persistencia de sesión

### 📊 Dashboard Interactivo
- KPIs animados en tiempo real
- Gráficas interactivas (Recharts)
- Filtros globales dinámicos
- Estadísticas por país, género, fechas
- Heatmaps y tendencias

### 🗺️ Mapas y Georreferenciación
- Mapas interactivos con Leaflet
- Recorridos en tiempo real
- Heatmaps geográficos
- Marcadores dinámicos

### 💎 Sistema de Descuentos
- Niveles: Bronce, Plata, Oro, Platino
- Progress bars animados
- Beneficios automáticos
- Badges y notificaciones

### 📋 Tablas Enterprise
- Paginación, ordenamiento, filtros
- Búsqueda en tiempo real
- Export CSV/Excel/PDF
- Acciones masivas
- Selección múltiple

### 🎯 Perfil de Usuario
- Gestión completa de perfiles
- Historial de viajes
- Estadísticas personales
- Configuración de privacidad

## KPIs y Métricas

- **Usuarios Activos**: Seguimiento de engagement
- **Viajes Completados/Cancelados**: Eficiencia operacional
- **Ingresos Totales**: Revenue tracking
- **Clientes Frecuentes**: Lealtad y retención
- **Tiempo Promedio**: Optimización de procesos
- **Rutas Populares**: Planificación estratégica
- **País Más Activo**: Expansión de mercado

## Manejo de Volumen Masivo (10M+ Registros)

### Optimizaciones Implementadas

1. **Índices de Base de Datos**:
   - Índice en `correo` para búsquedas rápidas de duplicados
   - Índice compuesto en `(pais, fecha_registro)` para consultas geográficas
   - Índice en `fecha_registro` para filtros temporales

2. **Paginación Eficiente**:
   - Uso de `OFFSET` y `LIMIT` con índices para consultas rápidas
   - Metadata completa de paginación en respuestas API
   - Límite máximo de 1000 registros por página

3. **Validaciones Estrictas**:
   - Algoritmo de Luhn para validación de tarjetas de crédito/débito
   - Validaciones Pydantic para integridad de datos
   - Manejo de excepciones con códigos HTTP apropiados

4. **Arquitectura Escalable**:
   - Separación de servicios (API, Dashboard, DB)
   - Conexiones a BD gestionadas automáticamente
   - Logs estructurados para monitoreo

### Performance Esperada
- Carga inicial: ~30-45 minutos para 10M registros
- Consultas paginadas: <100ms para páginas típicas
- Búsquedas por índice: <10ms
- Memoria: ~2-3GB para el conjunto completo de datos

## Estructura del Proyecto

```
SkyAnalytics/
├── backend/
│   ├── main.py              # Instancia FastAPI (ensambla routers)
│   ├── database.py          # Engine, sesión, create_all opcional
│   ├── deps.py              # JWT → usuario activo
│   ├── core/                # settings, JWT helpers, hashing
│   ├── models/              # ORM (pasajeros, users, millas, …)
│   ├── schemas/             # Pydantic por dominio
│   ├── routers/             # health, auth, analytics, pasajeros, estadísticas
│   ├── services/            # reglas de negocio (auth, categorías, analytics)
│   ├── middleware/          # logging + errores globales
│   ├── scripts/seed_admin.py
│   └── alembic/             # migraciones PostgreSQL
├── dashboard/
│   ├── app.py, theme.py, api_client.py
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## API (resumen)

Todas las rutas de negocio requieren cabecera `Authorization: Bearer <token>` salvo `/`, `/health`, `/auth/login`, `/auth/register`, `/auth/forgot-password`.

### Auth
- `POST /auth/login` — body: `email`, `password`, `remember_me`
- `POST /auth/register`
- `GET /auth/me`
- `POST /auth/logout` (informativo; el token se invalida en cliente)
- `POST /auth/forgot-password` (respuesta genérica; listo para integrar email)

### Analytics (dashboard)
- `GET /analytics/resumen`
- `GET /analytics/por-pais`
- `GET /analytics/tendencia-mensual`
- `GET /analytics/pasajeros` — paginación por `cursor` + `q` + filtros de fecha/país

### Pasajeros / transacciones
- CRUD bajo `/pasajeros`, perfil `/pasajeros/perfil/{id}`, transacciones `/pasajeros/{id}/transacciones` y ruta de compatibilidad `/transacciones/{pasajero_id}`.

## 🚀 Despliegue en la Nube

### AWS (ECS con Fargate)
1. **Crear repositorio ECR**:
   ```bash
   aws ecr create-repository --repository-name skyanalytics-backend
   aws ecr create-repository --repository-name skyanalytics-dashboard
   ```

2. **Construir y subir imágenes**:
   ```bash
   # Login a ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

   # Backend
   docker build -t skyanalytics-backend ./backend
   docker tag skyanalytics-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/skyanalytics-backend:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/skyanalytics-backend:latest

   # Dashboard
   docker build -t skyanalytics-dashboard ./dashboard
   docker tag skyanalytics-dashboard:latest <account>.dkr.ecr.us-east-1.amazonaws.com/skyanalytics-dashboard:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/skyanalytics-dashboard:latest
   ```

3. **Crear cluster ECS y servicios** usando AWS Console o CLI.

### Azure (Container Instances)
1. **Crear grupo de recursos**:
   ```bash
   az group create --name skyanalytics-rg --location eastus
   ```

2. **Crear contenedores**:
   ```bash
   az container create --resource-group skyanalytics-rg --name skyanalytics \
     --image <registry>/skyanalytics-backend:latest --dns-name-label skyanalytics \
     --ports 8000 8501 --environment-variables DB_HOST=<db_host> DB_PASS=<password>
   ```

### Google Cloud (Cloud Run)
1. **Construir y subir a GCR**:
   ```bash
   gcloud builds submit --tag gcr.io/<project>/skyanalytics-backend ./backend
   gcloud builds submit --tag gcr.io/<project>/skyanalytics-dashboard ./dashboard
   ```

2. **Desplegar**:
   ```bash
   gcloud run deploy skyanalytics-backend --image gcr.io/<project>/skyanalytics-backend --platform managed --port 8000
   gcloud run deploy skyanalytics-dashboard --image gcr.io/<project>/skyanalytics-dashboard --platform managed --port 8501
   ```

## 🧪 Pruebas Unitarias

Ejecutar pruebas:
```bash
cd backend
pytest tests/
```

Las pruebas incluyen:
- Endpoints de autenticación
- CRUD de pasajeros
- Validaciones de datos
- Paginación

## 🎉 Resumen de Logros

Has construido un **ecosistema completo de nivel enterprise** que demuestra:

### 🏗️ Arquitectura y Backend
- **FastAPI**: API REST robusta con documentación automática (Swagger)
- **SQLAlchemy**: ORM avanzado con migraciones (Alembic)
- **Pydantic**: Validaciones estrictas y schemas tipados
- **PostgreSQL**: Base de datos relacional optimizada para big data

### 📊 Big Data y BI
- **10M registros**: Gestión eficiente de volumen masivo
- **Índices optimizados**: Consultas rápidas con paginación
- **Streamlit**: Dashboard interactivo con visualizaciones avanzadas
- **Pandas/Plotly**: Análisis y gráficos profesionales

### 🔒 Seguridad y Escalabilidad
- **JWT Authentication**: Autenticación segura para administradores
- **Redis Caching**: Optimización de performance para consultas pesadas
- **Docker**: Contenerización completa con multi-servicio
- **Testing**: Cobertura de pruebas unitarias

### ☁️ Despliegue Cloud-Ready
- **AWS/Azure/GCP**: Instrucciones para despliegue en la nube
- **Docker Compose**: Orquestación local y de producción
- **Variables de entorno**: Configuración segura

### 📈 KPIs y Business Intelligence
- **Categorización automática**: Lógica de negocio para segmentación
- **Métricas estratégicas**: Top países, tendencias, segmentación por tarjetas
- **Filtros dinámicos**: Análisis interactivo por fechas y países

Este proyecto representa un **producto de software profesional** listo para producción, demostrando dominio completo del stack moderno de desarrollo. 🚀