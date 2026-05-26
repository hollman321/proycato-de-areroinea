# 🤖 SkyAnalytics IA - Asistente Inteligente

## Descripción General

El módulo de **Inteligencia Artificial** de SkyAnalytics es un asistente virtual inteligente que ayuda a los usuarios a:

✅ Entender y navegar todas las vistas del sistema  
✅ Completar tareas paso a paso  
✅ Resolver dudas sobre funcionalidades  
✅ Recibir recomendaciones contextuales  
✅ Acceder a ayuda rápida y específica  

El asistente es **contextual** - detecta en qué módulo estás y proporciona respuestas relevantes.

---

## 📁 Estructura de Archivos Creados

### Backend

```
SkyAnalytics/backend/
├── services/
│   └── ia_service.py              ← Lógica del asistente IA
├── routers/
│   └── ia.py                      ← Endpoints API /ai/*
├── schemas/
│   └── ia.py                      ← Modelos Pydantic
└── main.py                        ← (Modificado) Incluye router IA
```

### Frontend

```
SkyAnalytics/frontend/src/
├── components/
│   └── ChatIA.tsx                 ← Componente chatbot flotante
├── services/
│   └── ia.ts                      ← Cliente API para IA
├── hooks/
│   └── useChatIA.ts               ← Hook personalizado
├── lib/
│   └── ia-config.ts               ← Configuración IA
└── layouts/
    └── DashboardLayout.tsx        ← (Modificado) Integra ChatIA
```

---

## 🚀 Cómo Usar

### 1. **Iniciar Servicios**

#### Backend (FastAPI)
```powershell
cd c:\proycato-de-areroinea\SkyAnalytics\backend
py -m uvicorn main:app --host 0.0.0.0 --port 8001 --log-level info
```

#### Frontend (Next.js)
```powershell
cd c:\proycato-de-areroinea\SkyAnalytics\frontend
npm run dev
```

### 2. **Acceder a SkyAnalytics**

1. Abre tu navegador en `http://localhost:3000`
2. Inicia sesión con:
   - **Email:** `admin@skyanalytics.com`
   - **Contraseña:** `admin123`
3. En el dashboard, verás un **botón azul** en la esquina inferior derecha

### 3. **Usar el Chatbot IA**

**Botón Flotante:**
- Haz clic en el botón azul `💬` para abrir el chat
- Se abrirá una ventana con saludo inicial
- El chat incluye sugerencias de preguntas

**Interacción:**
- Escribe tu pregunta en el campo de texto
- Presiona **Enter** o haz clic en el botón de envío
- El asistente responderá inmediatamente

**Características:**
- **Sugerencias:** El chat sugiere preguntas relacionadas
- **Tips Rápidos:** Cada respuesta incluye tips útiles
- **Contexto:** El asistente sabe en qué módulo estás
- **Historial:** Se mantiene durante la sesión

---

## 💬 Ejemplos de Preguntas

### Panel Ejecutivo
- "¿Qué son los KPIs?"
- "¿Qué significan las métricas?"
- "¿Cómo interpretar las gráficas?"

### Operaciones
- "¿Cómo crear una operación?"
- "¿Cómo cambiar el estado de una operación?"
- "¿Cómo eliminar una operación?"

### Clientes
- "¿Cómo agregar un cliente?"
- "¿Qué datos necesito para un cliente?"
- "¿Cómo buscar un cliente?"

### Finanzas
- "¿Cómo ver mis ingresos?"
- "¿Cómo generar un reporte financiero?"
- "¿Qué incluye el balance?"

### Reportes
- "¿Cómo exportar datos a PDF?"
- "¿Cómo crear un reporte?"
- "¿Qué formatos están disponibles?"

### General
- "¿Cómo empiezo?"
- "¿Qué es SkyAnalytics?"
- "¿Quién puede ayudarme?"

---

## 🔧 Configuración Requerida

### Variables de Entorno

#### Backend (.env)
```env
DATABASE_URL=sqlite:///./skyanalytics_dev.db
SECRET_KEY=9k8L7m6N5o4P3q2R1s0T9u8V7w6X5y4Z3a2B1c0D9e8F7g6H5i4J3k2L1m0
JWT_ALGORITHM=HS256
CORS_ORIGINS=["*"]
LOG_LEVEL=info
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

---

## 📊 Endpoints API Disponibles

### Greeting
```
GET /ai/greeting
Respuesta: Saludo inicial + sugerencias
```

### Chat
```
POST /ai/chat
Body: {
  "message": "Tu pregunta aquí",
  "route": "/dashboard/operaciones"  (opcional)
}
Respuesta: Respuesta + intent + suggestions + tips
```

### Context
```
POST /ai/context
Body: {
  "route": "/dashboard/operaciones"
}
Respuesta: Información completa del módulo
```

### Help
```
POST /ai/help
Body: {
  "question": "Tu pregunta",
  "route": "/dashboard"  (opcional)
}
Respuesta: Respuesta detallada + tips
```

### History
```
GET /ai/history?limit=10
Respuesta: Historial de conversación
```

### Clear History
```
POST /ai/clear-history
Respuesta: Confirmación
```

### Modules
```
GET /ai/modules
Respuesta: Lista de todos los módulos disponibles
```

### Quick Links
```
GET /ai/quick-links/{module}
Respuesta: Links rápidos para un módulo específico
```

---

## 🧠 Intenciones Detectadas

El asistente automáticamente detecta qué tipo de pregunta haces:

- **help** → Preguntas sobre cómo hacer algo
- **navigate** → Preguntas sobre dónde ir
- **create** → Preguntas sobre crear elementos
- **edit** → Preguntas sobre editar
- **delete** → Preguntas sobre eliminar
- **export** → Preguntas sobre exportar datos
- **search** → Preguntas sobre buscar
- **general** → Otras preguntas

---

## 🎨 Características de la UI/UX

### Botón Flotante
- Ubicación: Esquina inferior derecha
- Color: Gradiente azul
- Icono: Cambia entre `💬` y `✕` según estado
- Animación: Escala suave al pasar el mouse

### Ventana del Chat
- Tamaño: 384px de ancho (w-96)
- Altura máxima: 600px
- Tema: Oscuro profesional (Slate 900)
- Animación: Fade + Scale al abrir/cerrar

### Mensajes
- **Usuario:** Azul claro (right-aligned)
- **IA:** Gris oscuro (left-aligned)
- Timestamp: Incluido automáticamente
- Sugerencias: Aparecen bajo respuestas
- Tips: Se muestran en color azul

### Input
- Diseño: Barra moderna con botón de envío
- Placeholder: "Escribe tu pregunta..."
- Estado: Se desactiva mientras se procesa
- Enter: Envía automáticamente

---

## 🔄 Flujo de Conversación

```
1. Usuario abre el chat
   ↓
2. Se carga saludo inicial con sugerencias
   ↓
3. Usuario escribe pregunta o hace clic en sugerencia
   ↓
4. Frontend envía POST /ai/chat con mensaje + ruta actual
   ↓
5. Backend procesa con ia_service:
   - Detecta intención
   - Obtiene contexto del módulo
   - Busca en base de conocimiento
   - Genera respuesta
   ↓
6. Frontend recibe respuesta con:
   - Mensaje principal
   - Intención detectada
   - Tips rápidos
   - Sugerencias para siguiente pregunta
   ↓
7. Se muestra en la UI con animaciones
   ↓
8. Ciclo se repite para siguiente pregunta
```

---

## 🛠️ Personalización

### Agregar Nuevas Preguntas

Edita `backend/services/ia_service.py`:

```python
COMMON_QUESTIONS = {
    "operaciones": {
        "¿nueva pregunta?": "Nueva respuesta aquí"
    }
}
```

### Agregar Nuevo Módulo

```python
SYSTEM_KNOWLEDGE = {
    "nuevo_modulo": {
        "title": "Título del Módulo",
        "description": "Descripción...",
        "features": [...],
        "actions": [...],
        "tips": [...]
    }
}
```

### Cambiar Frases Motivacionales

```python
MOTIVATIONAL_PHRASES = [
    "Tu saludo personalizado aquí",
    "Otro saludo..."
]
```

---

## 🧪 Pruebas

### Test 1: Saludo Inicial
1. Abre el chat
2. Verifica que aparezca saludo + 5 sugerencias

### Test 2: Pregunta en Dashboard
1. Estando en `/dashboard`
2. Pregunta: "¿Qué son los KPIs?"
3. Verifica respuesta contextual

### Test 3: Pregunta en Operaciones
1. Navega a `/dashboard/operaciones`
2. Pregunta: "¿Cómo crear una operación?"
3. Verifica tips específicos del módulo

### Test 4: Sugerencias
1. Haz cualquier pregunta
2. Verifica que haya sugerencias relacionadas
3. Haz clic en una sugerencia
4. Verifica que se procese como pregunta

### Test 5: Historial
1. Haz 3-4 preguntas
2. Abre DevTools → Network
3. GET `/ai/history` debe retornar todos los mensajes

### Test 6: Intenciones
- "crear cliente" → intent: "create"
- "¿dónde voy?" → intent: "navigate"
- "ayuda" → intent: "help"

---

## 🐛 Solución de Problemas

### El botón no aparece
- Verifica que el componente `ChatIA` esté en `DashboardLayout`
- Revisa la consola del navegador (DevTools)
- Asegúrate de que Framer Motion esté instalado

### El chat no responde
- Verifica que el backend esté corriendo en puerto 8001
- Revisa que `/ai/greeting` retorne datos
- Comprueba CORS en backend

### Las sugerencias no aparecen
- Las sugerencias solo aparecen si hay respuestas
- Verifica que la respuesta incluya `suggestions` field

### Error de autenticación
- Asegúrate de estar logueado
- El token JWT debe estar en localStorage

---

## 📈 Estadísticas de Implementación

- **Archivos Creados:** 7
- **Archivos Modificados:** 2
- **Líneas de Código Backend:** ~350
- **Líneas de Código Frontend:** ~600
- **Endpoints API:** 8
- **Módulos Soportados:** 9
- **Preguntas Predefinidas:** 40+
- **Intenciones Detectadas:** 7

---

## 🎯 Características Implementadas

✅ Chat flotante moderno  
✅ Historial de conversaciones  
✅ Respuestas rápidas contextuales  
✅ Mensajes automáticos  
✅ Animaciones suaves  
✅ Diseño responsive  
✅ Integración real con backend  
✅ API completa funcional  
✅ Contexto dinámico por ruta  
✅ Detección automática de intenciones  
✅ Tips y sugerencias inteligentes  
✅ Base de conocimiento completa  

---

## 📝 Notas Importantes

- El asistente IA es completamente funcional sin necesidad de APIs externas
- La base de conocimiento está hardcodeada en `ia_service.py`
- El contexto se actualiza automáticamente según la ruta del usuario
- El historial se limpia al cerrar sesión
- Las respuestas se optimizan según el módulo actual

---

## 🚀 Próximas Mejoras Sugeridas

- Integración con OpenAI/Claude para IA más inteligente
- Persistencia de historial en base de datos
- Analytics de preguntas más frecuentes
- Sugerencias basadas en ML
- Multi-idioma
- Voz (text-to-speech)
- Feedback de usuarios

---

**¡Tu asistente IA está listo para ayudar! 🤖✨**
