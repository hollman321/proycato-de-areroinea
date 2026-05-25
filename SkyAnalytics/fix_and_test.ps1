# Script para arreglar BD y probar backend
$ErrorActionPreference = 'Continue'

Write-Host "=== Paso 1: Insertar tenant por defecto ===" -ForegroundColor Cyan
docker compose exec -T db psql -U admin -d skyanalytics -c "INSERT INTO tenants (id, name, slug, region, is_active, created_at) VALUES (1, 'Default Tenant', 'default', 'Global', true, NOW())"
Write-Host "Salida anterior completada." -ForegroundColor Green

Write-Host "`n=== Paso 2: Verificar tenant creado ===" -ForegroundColor Cyan
docker compose exec -T db psql -U admin -d skyanalytics -c "SELECT * FROM tenants WHERE id=1"
Write-Host "Verificacion completada." -ForegroundColor Green

Write-Host "`n=== Paso 3: Añadir columna tenant_id a users ===" -ForegroundColor Cyan
docker compose exec -T db psql -U admin -d skyanalytics -c "ALTER TABLE users ADD COLUMN IF NOT EXISTS tenant_id integer DEFAULT 1 REFERENCES tenants(id)"
Write-Host "Columna añadida." -ForegroundColor Green

Write-Host "`n=== Paso 4: Verificar estructura de users ===" -ForegroundColor Cyan
docker compose exec -T db psql -U admin -d skyanalytics -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users' ORDER BY ordinal_position"
Write-Host "Estructura verificada." -ForegroundColor Green

Write-Host "`n=== Paso 5: Reiniciar backend ===" -ForegroundColor Cyan
docker compose up -d --build backend
Write-Host "Backend reiniciado." -ForegroundColor Green

Write-Host "`n=== Esperando 5 segundos para que backend inicie ===" -ForegroundColor Cyan
Start-Sleep -Seconds 5

Write-Host "`n=== Paso 6: Ver estado de contenedores ===" -ForegroundColor Cyan
docker compose ps

Write-Host "`n=== Paso 7: Ver últimos 100 logs del backend ===" -ForegroundColor Cyan
docker compose logs backend --tail 100

Write-Host "`n=== Paso 8: Probar endpoints ===" -ForegroundColor Cyan
Write-Host "Probando http://localhost:8000/health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod http://localhost:8000/health -TimeoutSec 5
    Write-Host "✓ Backend respondió: $healthResponse" -ForegroundColor Green
}
catch {
    Write-Host "✗ Backend NO respondió: $_" -ForegroundColor Red
}

Write-Host "`nProbando http://localhost:3000..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest http://localhost:3000 -TimeoutSec 5
    Write-Host "✓ Frontend respondió con status: $($frontendResponse.StatusCode)" -ForegroundColor Green
}
catch {
    Write-Host "✗ Frontend NO respondió: $_" -ForegroundColor Red
}

Write-Host "`n=== RESUMEN FINAL ===" -ForegroundColor Cyan
Write-Host "Script completado. Revisa los outputs anteriores para cualquier error." -ForegroundColor Green
