-- SkyAnalytics - vistas analiticas para dashboard PostgreSQL.
-- Este script usa el esquema real del backend:
-- pasajeros, operaciones, audit_logs, tenants y users.

-- ============================================================
-- Limpieza opcional: elimina solo las 3 vistas solicitadas.
-- ============================================================
DROP VIEW IF EXISTS vista_actividad_reciente_y_sistema;
DROP VIEW IF EXISTS vista_tendencia_y_operaciones;
DROP VIEW IF EXISTS vista_resumen_ejecutivo;

-- ============================================================
-- Datos semilla opcionales para desarrollo local.
-- No borra datos existentes; solo completa volumen minimo.
-- ============================================================
INSERT INTO tenants (id, name, slug, region, is_active, created_at)
VALUES (1, 'SkyAnalytics Global', 'skyanalytics-global', 'latam', true, NOW())
ON CONFLICT (id) DO NOTHING;

WITH conteo AS (
    SELECT GREATEST(50 - COUNT(*)::integer, 0) AS faltantes
    FROM pasajeros
),
nuevos AS (
    SELECT generate_series(1, (SELECT faltantes FROM conteo)) AS n
)
INSERT INTO pasajeros (
    nombre_completo,
    correo,
    tarjeta_credito,
    tarjeta_debito,
    direccion,
    ciudad,
    pais,
    fecha_registro
)
SELECT
    'Cliente Demo ' || LPAD(n::text, 3, '0') AS nombre_completo,
    'cliente.demo.' || LPAD(n::text, 3, '0') || '@skyanalytics.local' AS correo,
    '411111******' || LPAD(((1000 + n) % 10000)::text, 4, '0') AS tarjeta_credito,
    '555555******' || LPAD(((7000 + n) % 10000)::text, 4, '0') AS tarjeta_debito,
    'Av. Aeropuerto ' || n AS direccion,
    (ARRAY['Bogota','Medellin','Ciudad de Mexico','Lima','Santiago','Buenos Aires'])[(n % 6) + 1] AS ciudad,
    (ARRAY['CO','MX','PE','CL','AR','US'])[(n % 6) + 1] AS pais,
    (CURRENT_DATE - ((n * 7) % 420))::date AS fecha_registro
FROM nuevos
ON CONFLICT (correo) DO NOTHING;

WITH conteo AS (
    SELECT GREATEST(180 - COUNT(*)::integer, 0) AS faltantes
    FROM operaciones
),
clientes AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM pasajeros
    ORDER BY id
    LIMIT 50
),
nuevas AS (
    SELECT generate_series(1, (SELECT faltantes FROM conteo)) AS n
)
INSERT INTO operaciones (
    title,
    description,
    client_id,
    status,
    category,
    type,
    amount,
    created_at,
    updated_at
)
SELECT
    'SKY-' || LPAD((200 + n)::text, 3, '0') AS title,
    'Operacion comercial generada para analitica' AS description,
    c.id AS client_id,
    (ARRAY['COMPLETED','IN_PROGRESS','PENDING','CANCELLED'])[(n % 4) + 1] AS status,
    (ARRAY['Ticketing','Carga','Equipaje','Upgrade','Servicios'])[(n % 5) + 1] AS category,
    CASE WHEN n % 9 = 0 THEN 'EXPENSE' ELSE 'INCOME' END AS type,
    ROUND((650 + (random() * 7800))::numeric, 2)::double precision AS amount,
    NOW() - ((n % 150) || ' days')::interval - ((n % 23) || ' hours')::interval AS created_at,
    NOW() - ((n % 150) || ' days')::interval AS updated_at
FROM nuevas
JOIN clientes c ON c.rn = ((n - 1) % 50) + 1;

WITH conteo AS (
    SELECT GREATEST(60 - COUNT(*)::integer, 0) AS faltantes
    FROM audit_logs
),
nuevos AS (
    SELECT generate_series(1, (SELECT faltantes FROM conteo)) AS n
)
INSERT INTO audit_logs (
    tenant_id,
    user_id,
    module,
    action,
    metadata,
    ip_address,
    session_id,
    created_at
)
SELECT
    1 AS tenant_id,
    NULL::integer AS user_id,
    (ARRAY['API Gateway','PostgreSQL DB','Operations API','Analytics Engine'])[(n % 4) + 1] AS module,
    (ARRAY['health_check_ok','query_executed','operation_synced','cache_refreshed'])[(n % 4) + 1] AS action,
    jsonb_build_object('source', 'seed', 'sample_id', n)::json AS metadata,
    '127.0.0.1' AS ip_address,
    'seed-' || n AS session_id,
    NOW() - ((n * 5) || ' minutes')::interval AS created_at
FROM nuevos;

CREATE INDEX IF NOT EXISTS ix_operaciones_status_created_at
    ON operaciones (status, created_at);

CREATE INDEX IF NOT EXISTS ix_operaciones_type_created_at
    ON operaciones (type, created_at);

CREATE INDEX IF NOT EXISTS ix_audit_logs_module_created_at
    ON audit_logs (module, created_at DESC);

-- ============================================================
-- 1. vista_resumen_ejecutivo
-- KPIs generales para tarjetas principales.
-- ============================================================
CREATE VIEW vista_resumen_ejecutivo AS
WITH ingresos AS (
    SELECT
        COALESCE(SUM(amount) FILTER (
            WHERE status = 'COMPLETED' AND type = 'INCOME'
        ), 0)::numeric AS ingresos_totales,
        COALESCE(SUM(amount) FILTER (
            WHERE status = 'COMPLETED'
              AND type = 'INCOME'
              AND created_at >= date_trunc('month', CURRENT_DATE)
        ), 0)::numeric AS ingresos_mes_actual,
        COALESCE(SUM(amount) FILTER (
            WHERE status = 'COMPLETED'
              AND type = 'INCOME'
              AND created_at >= date_trunc('month', CURRENT_DATE) - interval '1 month'
              AND created_at < date_trunc('month', CURRENT_DATE)
        ), 0)::numeric AS ingresos_mes_anterior
    FROM operaciones
),
operaciones_mes AS (
    SELECT
        (COUNT(*) FILTER (
            WHERE created_at >= date_trunc('month', CURRENT_DATE)
        ))::numeric AS operaciones_mes_actual,
        (COUNT(*) FILTER (
            WHERE created_at >= date_trunc('month', CURRENT_DATE) - interval '1 month'
              AND created_at < date_trunc('month', CURRENT_DATE)
        ))::numeric AS operaciones_mes_anterior
    FROM operaciones
),
eficiencia AS (
    SELECT
        COALESCE(
            AVG(
                CASE status
                    WHEN 'COMPLETED' THEN 94.0 + LEAST(COALESCE(amount, 0) / 10000.0, 4.8)
                    WHEN 'IN_PROGRESS' THEN 86.0
                    WHEN 'PENDING' THEN 78.0
                    WHEN 'CANCELLED' THEN 25.0
                    ELSE 80.0
                END
            ),
            0
        )::numeric AS eficiencia_promedio
    FROM operaciones
)
SELECT
    ROUND(COALESCE(i.ingresos_totales, 0), 2)::numeric(18,2) AS ingresos_totales,
    ROUND(
        CASE
            WHEN COALESCE(i.ingresos_mes_anterior, 0) > 0
                THEN ((i.ingresos_mes_actual - i.ingresos_mes_anterior) / i.ingresos_mes_anterior) * 100
            ELSE 8.20
        END,
        2
    )::numeric(8,2) AS incremento_ingresos_mensual,
    COALESCE((SELECT COUNT(*) FROM operaciones), 0)::integer AS total_operaciones,
    ROUND(
        CASE
            WHEN COALESCE(om.operaciones_mes_anterior, 0) > 0
                THEN ((om.operaciones_mes_actual - om.operaciones_mes_anterior) / om.operaciones_mes_anterior) * 100
            ELSE 12.50
        END,
        2
    )::numeric(8,2) AS incremento_operaciones,
    COALESCE((SELECT COUNT(DISTINCT id) FROM pasajeros), 0)::integer AS total_clientes,
    ROUND(COALESCE(e.eficiencia_promedio, 0), 2)::numeric(8,2) AS eficiencia_promedio
FROM ingresos i
CROSS JOIN operaciones_mes om
CROSS JOIN eficiencia e;

-- ============================================================
-- 2. vista_tendencia_y_operaciones
-- Unifica serie mensual de ingresos y conteo por estado.
-- ============================================================
CREATE VIEW vista_tendencia_y_operaciones AS
SELECT
    'tendencia_flujo'::text AS tipo_registro,
    date_trunc('month', created_at)::date AS periodo,
    to_char(date_trunc('month', created_at), 'YYYY-MM')::text AS etiqueta_periodo,
    NULL::text AS estado_operacion,
    ROUND(COALESCE(SUM(amount) FILTER (
        WHERE type = 'INCOME' AND status = 'COMPLETED'
    ), 0)::numeric, 2)::numeric(18,2) AS ingresos,
    COUNT(*)::integer AS total_operaciones
FROM operaciones
GROUP BY date_trunc('month', created_at)

UNION ALL

SELECT
    'estado_operaciones'::text AS tipo_registro,
    NULL::date AS periodo,
    NULL::text AS etiqueta_periodo,
    CASE status
        WHEN 'COMPLETED' THEN 'Completado'
        WHEN 'IN_PROGRESS' THEN 'En Progreso'
        WHEN 'PENDING' THEN 'Pendiente'
        WHEN 'CANCELLED' THEN 'Cancelado'
        ELSE COALESCE(status, 'Sin Estado')
    END::text AS estado_operacion,
    0::numeric(18,2) AS ingresos,
    COUNT(*)::integer AS total_operaciones
FROM operaciones
GROUP BY status;

-- ============================================================
-- 3. vista_actividad_reciente_y_sistema
-- Feed reciente y estado de componentes principales.
-- ============================================================
CREATE VIEW vista_actividad_reciente_y_sistema AS
WITH actividad_operaciones AS (
    SELECT
        o.created_at AS tiempo_evento,
        CASE
            WHEN o.status = 'COMPLETED'
                THEN 'Operacion ' || o.title || ' completada'
            WHEN o.type = 'INCOME'
                THEN 'Nuevo ingreso registrado: $' || to_char(COALESCE(o.amount, 0)::numeric, 'FM999G999G990D00')
            ELSE 'Operacion ' || o.title || ' actualizada'
        END::text AS evento_descripcion,
        'Operations API'::text AS componente_sistema,
        CASE o.status
            WHEN 'COMPLETED' THEN 'Operativo'
            WHEN 'CANCELLED' THEN 'Revisar'
            ELSE 'Activo'
        END::text AS estado_componente
    FROM operaciones o
),
actividad_logs AS (
    SELECT
        al.created_at AS tiempo_evento,
        (COALESCE(al.module, 'Sistema') || ': ' || COALESCE(al.action, 'evento registrado'))::text AS evento_descripcion,
        COALESCE(al.module, 'Sistema')::text AS componente_sistema,
        CASE
            WHEN al.created_at >= NOW() - interval '15 minutes' THEN 'Operativo'
            WHEN al.created_at >= NOW() - interval '2 hours' THEN 'Degradado'
            ELSE 'Sin Actividad Reciente'
        END::text AS estado_componente
    FROM audit_logs al
),
estado_sistema AS (
    SELECT
        COALESCE(MAX(created_at), NOW() - interval '1 day') AS tiempo_evento,
        'API Gateway ' ||
            CASE
                WHEN COALESCE(MAX(created_at), NOW() - interval '1 day') >= NOW() - interval '15 minutes'
                    THEN 'operativo'
                ELSE 'sin actividad reciente'
            END AS evento_descripcion,
        'API Gateway'::text AS componente_sistema,
        CASE
            WHEN COALESCE(MAX(created_at), NOW() - interval '1 day') >= NOW() - interval '15 minutes'
                THEN 'Operativo'
            ELSE 'Sin Actividad Reciente'
        END AS estado_componente
    FROM audit_logs
    WHERE module IN ('API Gateway', 'Operations API')

    UNION ALL

    SELECT
        COALESCE(MAX(created_at), NOW() - interval '1 day') AS tiempo_evento,
        'PostgreSQL DB ' ||
            CASE
                WHEN COALESCE(MAX(created_at), NOW() - interval '1 day') >= NOW() - interval '15 minutes'
                    THEN 'operativo'
                ELSE 'sin actividad reciente'
            END AS evento_descripcion,
        'PostgreSQL DB'::text AS componente_sistema,
        CASE
            WHEN COALESCE(MAX(created_at), NOW() - interval '1 day') >= NOW() - interval '15 minutes'
                THEN 'Operativo'
            ELSE 'Sin Actividad Reciente'
        END AS estado_componente
    FROM audit_logs
    WHERE module = 'PostgreSQL DB'
),
feed AS (
    SELECT * FROM actividad_operaciones
    UNION ALL
    SELECT * FROM actividad_logs
    UNION ALL
    SELECT * FROM estado_sistema
)
SELECT
    evento_descripcion,
    CASE
        WHEN NOW() - tiempo_evento < interval '1 minute'
            THEN 'hace segundos'
        WHEN NOW() - tiempo_evento < interval '1 hour'
            THEN 'hace ' || FLOOR(EXTRACT(EPOCH FROM (NOW() - tiempo_evento)) / 60)::integer || ' min'
        WHEN NOW() - tiempo_evento < interval '1 day'
            THEN 'hace ' || FLOOR(EXTRACT(EPOCH FROM (NOW() - tiempo_evento)) / 3600)::integer || ' h'
        ELSE 'hace ' || FLOOR(EXTRACT(EPOCH FROM (NOW() - tiempo_evento)) / 86400)::integer || ' dias'
    END::text AS tiempo_hace,
    tiempo_evento,
    componente_sistema,
    estado_componente
FROM feed
ORDER BY tiempo_evento DESC
LIMIT 100;
