# Configuración de Variables de Entorno en Vercel

Para que la aplicación funcione en Vercel, debes configurar estas variables de entorno:

## Pasos:

1. Ve a https://vercel.com/dashboard
2. Selecciona tu proyecto
3. Ve a **Settings → Environment Variables**
4. Agrega las siguientes variables:

### Variables Requeridas:

```
SECRET_KEY=cambia-esto-por-un-secreto-largo-y-aleatorio-minimo-32-caracteres
JWT_ALGORITHM=HS256
DATABASE_URL=sqlite:///skyanalytics.db
CORS_ORIGINS=*
LOG_LEVEL=INFO
OPENAI_API_KEY=(déjalo vacío o agrega tu clave)
OPENAI_MODEL=gpt-4o-mini
```

### Para Producción (Importante):
- Usa una base de datos PostgreSQL real en lugar de SQLite
- Cambia `SECRET_KEY` por algo seguro y aleatorio
- Establece `CORS_ORIGINS` específicamente (no uses `*` en producción)

## Base de Datos Recomendada:
- Vercel PostgreSQL (https://vercel.com/storage/postgres)
- Supabase (https://supabase.com)
- Railway.app
- PlanetScale

Una vez configuradas, Vercel redesplegará automáticamente.
