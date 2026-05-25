-- Sincronizar base de datos con modelos
-- 1. Crear tenant por defecto si no existe
INSERT INTO tenants (id, name, slug, region, is_active, created_at)
VALUES (
        1,
        'Default Tenant',
        'default',
        'Global',
        true,
        NOW()
    ) ON CONFLICT (id) DO NOTHING;
-- 2. Añadir columna tenant_id a users si no existe
ALTER TABLE users
ADD COLUMN IF NOT EXISTS tenant_id integer DEFAULT 1 REFERENCES tenants(id);
-- 3. Verificar estructura
SELECT '--- TENANTS TABLE ---' as status;
SELECT *
FROM tenants;
SELECT '--- USERS TABLE STRUCTURE ---' as status;
\ d users
SELECT '--- USERS COUNT ---' as status;
SELECT COUNT(*) as user_count
FROM users;