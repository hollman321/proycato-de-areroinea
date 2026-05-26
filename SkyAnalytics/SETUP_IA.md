# ⚙️ Guía de Instalación y Configuración del Módulo IA

## 1. Verificar Dependencias

### Backend
Las siguientes librerías ya están instaladas:
```
fastapi==0.115.0
sqlalchemy==2.0.28
pydantic==2.8.2
```

No necesitas instalar nada adicional.

### Frontend
Las siguientes librerías ya están instaladas:
```
framer-motion (^11.0.0)
lucide-react (^0.394.0)
axios (para HTTP requests)
```

Verifica en `package.json`:
```bash
cd frontend
npm list framer-motion lucide-react
```

Si falta algo:
```bash
npm install framer-motion lucide-react
```

---

## 2. Estructura del Backend

### Archivo: `backend/services/ia_service.py`
**Responsabilidad:** Lógica central del asistente IA

**Componentes principales:**
- `SYSTEM_KNOWLEDGE` - Base de conocimiento de módulos
- `COMMON_QUESTIONS` - Q&A predefinidas
- `MOTIVATIONAL_PHRASES` - Saludos iniciales

**Métodos clave:**
```python
ia_service.answer_question(question, route)  # Responder pregunta
ia_service.get_context_by_route(route)       # Contexto del módulo
ia_service.detect_intent(message)            # Detectar tipo de pregunta
ia_service.add_to_history(message)           # Guardar en historial
```

### Archivo: `backend/routers/ia.py`
**Responsabilidad:** Endpoints HTTP/REST

**Endpoints disponibles:**
```
GET  /ai/greeting              - Saludo inicial
POST /ai/chat                  - Enviar mensaje
POST /ai/context               - Contexto del módulo
POST /ai/help                  - Ayuda específica
GET  /ai/history               - Historial
POST /ai/clear-history         - Limpiar historial
GET  /ai/modules               - Lista de módulos
GET  /ai/quick-links/{module}  - Links rápidos
```

### Archivo: `backend/schemas/ia.py`
**Responsabilidad:** Modelos Pydantic para validación

**Schemas principales:**
- `IAMessageRequest` - Validar mensaje del usuario
- `IAMessageResponse` - Estructura de respuesta
- `IAContextResponse` - Información del módulo
- `IAGreetingResponse` - Saludo inicial

---

## 3. Estructura del Frontend

### Archivo: `frontend/src/components/ChatIA.tsx`
**Responsabilidad:** Componente visual del chatbot

**Características:**
- Botón flotante en esquina inferior derecha
- Ventana de chat modal
- Historial de mensajes
- Input con auto-send en Enter
- Sugerencias contextuales
- Tips informativos
- Animaciones suaves

**Props:**
```typescript
interface ChatIAProps {
  currentRoute?: string  // Ruta actual para contexto
}
```

### Archivo: `frontend/src/services/ia.ts`
**Responsabilidad:** Cliente HTTP para endpoints IA

**Métodos disponibles:**
```typescript
iaService.getGreeting()           // GET /ai/greeting
iaService.sendMessage(msg, route) // POST /ai/chat
iaService.getContext(route)       // POST /ai/context
iaService.getHelp(question)       // POST /ai/help
iaService.getHistory(limit)       // GET /ai/history
iaService.clearHistory()          // POST /ai/clear-history
iaService.getAllModules()         // GET /ai/modules
iaService.getQuickLinks(module)   // GET /ai/quick-links/{module}
```

### Archivo: `frontend/src/hooks/useChatIA.ts`
**Responsabilidad:** Hook personalizado para manejo de estado

**Métodos:**
```typescript
const {
  messages,                // Lista de mensajes
  isLoading,              // Cargando
  error,                  // Errores
  sendMessage,            // Enviar mensaje
  getModuleContext,       // Obtener contexto
  getHelp,               // Obtener ayuda
  loadGreeting,          // Cargar saludo
  // ... más métodos
} = useChatIA('/dashboard/operaciones')
```

### Archivo: `frontend/src/lib/ia-config.ts`
**Responsabilidad:** Configuración centralizada

**Contiene:**
- `API_BASE_URL` - URL del backend
- `AI_ENDPOINTS` - Rutas de endpoints

---

## 4. Integración en Layout

### Cambio en `frontend/src/layouts/DashboardLayout.tsx`

**Import agregado:**
```typescript
import { ChatIA } from '@/components/ChatIA'
```

**Componente agregado en return:**
```typescript
<ChatIA currentRoute={pathname} />
```

**Ubicación:** Después del `main` y antes del cierre del `div` principal.

---

## 5. Configuración de Variables de Entorno

### Backend

Archivo: `SkyAnalytics/.env` o `backend/.env`

```env
# Database
DATABASE_URL=sqlite:///./skyanalytics_dev.db

# JWT
SECRET_KEY=9k8L7m6N5o4P3q2R1s0T9u8V7w6X5y4Z3a2B1c0D9e8F7g6H5i4J3k2L1m0
JWT_ALGORITHM=HS256

# CORS (para frontend)
CORS_ORIGINS=["*"]

# Logging
LOG_LEVEL=info
```

### Frontend

Archivo: `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

---

## 6. Inicialización Paso a Paso

### Paso 1: Inicia el Backend

```powershell
cd c:\proycato-de-areroinea\SkyAnalytics\backend

# Activa virtual env (si no está activo)
..\..\.venv\Scripts\Activate.ps1

# Inicia servidor
py -m uvicorn main:app --host 0.0.0.0 --port 8001 --log-level info
```

**Esperado:**
```
INFO:     Application startup complete
Uvicorn running on http://0.0.0.0:8001
```

### Paso 2: Inicia el Frontend

```powershell
cd c:\proycato-de-areroinea\SkyAnalytics\frontend

# Instala dependencias (si es primera vez)
npm install

# Inicia dev server
npm run dev
```

**Esperado:**
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully
```

### Paso 3: Accede a la Aplicación

1. Abre navegador en: `http://localhost:3000`
2. Login con:
   - Email: `admin@skyanalytics.com`
   - Contraseña: `admin123`
3. Busca botón azul flotante en esquina inferior derecha
4. Haz clic para abrir el chat IA

---

## 7. Prueba del Chatbot

### Test de Conexión

1. Abre DevTools (F12)
2. Ve a Network
3. Abre el chat IA
4. Deberías ver una petición GET a `/ai/greeting`
5. Respuesta debe incluir `greeting` y `suggestions`

### Test de Interacción

1. Escribe: "¿Cómo crear una operación?"
2. En DevTools → Network, busca `POST /ai/chat`
3. El payload debe incluir:
   ```json
   {
     "message": "¿Cómo crear una operación?",
     "route": "/dashboard/operaciones"
   }
   ```
4. La respuesta debe incluir:
   ```json
   {
     "message": "Para crear una nueva operación...",
     "intent": "help",
     "suggestions": [...],
     "quick_tips": [...]
   }
   ```

---

## 8. Archivos Modificados

### `backend/main.py`
**Cambios:**
- Línea 19: Agregado `import ia` en routers
- Línea 75: Agregado `app.include_router(ia.router)`

**Antes:**
```python
from routers import (
    admin,
    analytics,
    auth,
    ...
)
```

**Después:**
```python
from routers import (
    admin,
    analytics,
    auth,
    ia,  # ← AGREGADO
    ...
)
```

### `frontend/src/layouts/DashboardLayout.tsx`
**Cambios:**
- Línea 8: Agregado `import { ChatIA }`
- Línea 183-184: Agregado `<ChatIA currentRoute={pathname} />`

---

## 9. Monitoreo y Debugging

### Logs del Backend

Mira los logs en la terminal del backend para ver:
```
INFO:     GET /ai/greeting - HTTP/1.1" 200
INFO:     POST /ai/chat - HTTP/1.1" 200
```

### DevTools del Frontend

En la consola del navegador:
```javascript
// Ver últimos mensajes
console.log(localStorage.getItem('auth-token'))

// Ver peticiones de red
// Ir a Network tab y filtrar por /ai/
```

### Errores Comunes

**Error: "net::ERR_CONNECTION_REFUSED"**
- El backend no está corriendo
- Solución: Inicia backend en puerto 8001

**Error: "401 Unauthorized"**
- Token JWT expirado o inválido
- Solución: Logout y login de nuevo

**Error: "CORS policy blocked"**
- CORS no configurado correctamente
- Solución: Verifica `CORS_ORIGINS=["*"]` en backend

**Error: "Module not found"**
- Falta instalar dependencias en frontend
- Solución: `npm install`

---

## 10. Métricas de Performance

### Tiempos esperados

- Saludo inicial: < 100ms
- Respuesta a pregunta: 50-200ms
- Apertura del chat: Instantáneo
- Cierre del chat: Instantáneo

### Si es lento

1. Verifica conexión de red
2. Abre DevTools → Performance tab
3. Registra el performance
4. Busca bottlenecks

---

## 11. Checklist de Implementación

- [x] Crear `backend/services/ia_service.py`
- [x] Crear `backend/routers/ia.py`
- [x] Crear `backend/schemas/ia.py`
- [x] Modificar `backend/main.py`
- [x] Crear `frontend/src/components/ChatIA.tsx`
- [x] Crear `frontend/src/services/ia.ts`
- [x] Crear `frontend/src/hooks/useChatIA.ts`
- [x] Crear `frontend/src/lib/ia-config.ts`
- [x] Modificar `frontend/src/layouts/DashboardLayout.tsx`
- [x] Documentación

---

## 12. Soporte y Contacto

Para reportar bugs o sugerencias:
1. Revisa los logs del backend
2. Abre DevTools del navegador
3. Copia el error exacto
4. Contacta al equipo de desarrollo

---

**¡Implementación completada! 🎉**
