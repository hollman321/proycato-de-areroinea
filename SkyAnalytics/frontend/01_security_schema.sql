-- Crear tipo ENUM para roles si no existe
DO $$ BEGIN CREATE TYPE user_role AS ENUM ('USER', 'ADMIN', 'EMPLOYEE', 'SUPERADMIN');
EXCEPTION
WHEN duplicate_object THEN null;
END $$;
-- Asegurar tabla de usuarios con constraints
ALTER TABLE users
ADD COLUMN IF NOT EXISTS role user_role DEFAULT 'USER',
    ADD COLUMN IF NOT EXISTS permissions JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;
-- Constraint de validación de integridad
DO $$ BEGIN
ALTER TABLE users
ADD CONSTRAINT check_valid_role CHECK (
        role IN ('USER', 'ADMIN', 'EMPLOYEE', 'SUPERADMIN')
    );
EXCEPTION
WHEN duplicate_object THEN null;
END $$;
-- Índice para búsquedas rápidas de auth
CREATE INDEX IF NOT EXISTS idx_users_email_role ON users(email, role);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);