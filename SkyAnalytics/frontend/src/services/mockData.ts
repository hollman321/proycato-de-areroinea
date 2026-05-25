export const mockDashboardResumen = {
    usuarios_activos: 1248,
    viajes_completados: 874,
    ingresos: 1385200,
    clientes_frecuentes: 523,
    pais_mas_activo: 'Colombia',
    tiempo_promedio: 142,
    rutas_populares: ['BOG - MIA', 'LAX - SFO', 'MAD - BCN', 'CDG - LHR', 'GRU - EZE'],
}

export const mockTendenciasMensuales = [
    { mes: 'Ene', valor: 820 },
    { mes: 'Feb', valor: 930 },
    { mes: 'Mar', valor: 1050 },
    { mes: 'Abr', valor: 1140 },
    { mes: 'May', valor: 1280 },
    { mes: 'Jun', valor: 1500 },
    { mes: 'Jul', valor: 1420 },
    { mes: 'Ago', valor: 1580 },
    { mes: 'Sep', valor: 1700 },
    { mes: 'Oct', valor: 1800 },
    { mes: 'Nov', valor: 1940 },
    { mes: 'Dic', valor: 2100 },
]

export const mockPaises = [
    { name: 'Colombia', value: 340, porcentaje: 23 },
    { name: 'México', value: 280, porcentaje: 18 },
    { name: 'España', value: 220, porcentaje: 15 },
    { name: 'Estados Unidos', value: 190, porcentaje: 12 },
    { name: 'Chile', value: 160, porcentaje: 9 },
    { name: 'Perú', value: 140, porcentaje: 8 },
]

export const mockAIRecommendations = {
    active_models: 4,
    accuracy: '91%',
    recommendations: [
        {
            id: 'rec-1',
            title: 'Optimizar capacidad de rutas premium',
            description: 'Ajustar frecuencias en rutas con alta demanda durante picos de vacaciones.',
            priority: 'Alta',
            impact: '+12% ocupación',
            confidence: '93%',
        },
        {
            id: 'rec-2',
            title: 'Reducir costes de combustible',
            description: 'Enrutar aeronaves con peso optimizado y evitar desvíos de viento.',
            priority: 'Media',
            impact: 'Ahorrar 6% en combustible',
            confidence: '88%',
        },
        {
            id: 'rec-3',
            title: 'Aumentar retención de clientes',
            description: 'Lanzar promociones segmentadas a viajeros frecuentes por región.',
            priority: 'Alta',
            impact: '+8% retención',
            confidence: '91%',
        },
    ],
}

export const mockFlightsSearch = {
    total: 15,
    items: [
        { pasajero_id: 1, pasajeros: 3, aeropuerto_salida: 'BOG', aeropuerto_llegada: 'MIA', pais_origen: 'Colombia', pais_destino: 'Estados Unidos', vuelos_historicos: 5 },
        { pasajero_id: 2, pasajeros: 1, aeropuerto_salida: 'LHR', aeropuerto_llegada: 'CDG', pais_origen: 'Reino Unido', pais_destino: 'Francia', vuelos_historicos: 2 },
        { pasajero_id: 3, pasajeros: 2, aeropuerto_salida: 'SFO', aeropuerto_llegada: 'LAX', pais_origen: 'Estados Unidos', pais_destino: 'Estados Unidos', vuelos_historicos: 8 },
        { pasajero_id: 4, pasajeros: 4, aeropuerto_salida: 'GRU', aeropuerto_llegada: 'EZE', pais_origen: 'Brasil', pais_destino: 'Argentina', vuelos_historicos: 6 },
    ],
}

export const mockPasajeros = {
    total: 12,
    items: [
        { id: 101, nombre_completo: 'María González', correo: 'maria.gonzalez@example.com', tarjeta_credito: '4111 1111 1111 1111', tarjeta_debito: '4111 1111 1111 1111', direccion: 'Cra 15 # 42-10', ciudad: 'Bogotá', pais: 'Colombia', fecha_registro: '2024-02-10' },
        { id: 102, nombre_completo: 'Lucas Martínez', correo: 'lucas.martinez@example.com', tarjeta_credito: '5555 4444 3333 2222', tarjeta_debito: '5555 4444 3333 2222', direccion: 'Av. Paulista 1000', ciudad: 'São Paulo', pais: 'Brasil', fecha_registro: '2024-03-22' },
        { id: 103, nombre_completo: 'Camila Rodríguez', correo: 'camila.rodriguez@example.com', tarjeta_credito: '4000 1234 5678 9010', tarjeta_debito: '4000 1234 5678 9010', direccion: 'Calle 100 # 20-30', ciudad: 'Medellín', pais: 'Colombia', fecha_registro: '2024-04-05' },
    ],
}

export const mockFinanceData = {
    monthly_revenue: 1285400,
    operational_costs: 640200,
    net_margin: 18.7,
    ytd: [
        { month: 'Ene', revenue: 980000 },
        { month: 'Feb', revenue: 1020000 },
        { month: 'Mar', revenue: 1080000 },
        { month: 'Abr', revenue: 1105000 },
        { month: 'May', revenue: 1152000 },
        { month: 'Jun', revenue: 1285400 },
    ],
    cash_cycle: 28,
    available_funds: 420000,
    savings_opportunity: 'Optimizar contratos de mantenimiento',
}

export const mockMonitoringStatus = {
    api_status: 'Healthy',
    database_status: 'Healthy',
    redis_status: 'Healthy',
    uptime: '99.97%',
    last_checked: 'Hace 2 minutos',
    traffic: [
        { time: '10:00', value: 45 },
        { time: '10:10', value: 52 },
        { time: '10:20', value: 48 },
        { time: '10:30', value: 62 },
        { time: '10:40', value: 55 },
        { time: '10:50', value: 60 },
    ],
}

export const mockMonitoringAlerts = {
    alerts: [
        { id: 'a1', severity: 'Alta', message: 'Latency elevada detectada en API de reservas', timestamp: '2026-05-22 10:45', status: 'Abierta' },
        { id: 'a2', severity: 'Media', message: 'Uso de CPU en servidor de datos cercano a límite', timestamp: '2026-05-22 10:32', status: 'Revisado' },
        { id: 'a3', severity: 'Alta', message: 'Fallo intermitente en integraciones de pago', timestamp: '2026-05-22 10:10', status: 'Abierta' },
    ],
}

export const mockMonitoringLogs = {
    logs: [
        { id: 'l1', action: 'Reiniciado servicio backend', user: 'admin', created_at: '2026-05-22 09:55' },
        { id: 'l2', action: 'Actualizada regla de workflows', user: 'alejandro', created_at: '2026-05-22 09:20' },
        { id: 'l3', action: 'Generado reporte financiero trimestral', user: 'marta', created_at: '2026-05-21 18:15' },
    ],
}

export const mockWorkflows = {
    workflows: [
        { id: 'w1', name: 'Carga inicial de datos', state: 'idle', last_run: '2026-05-21 14:20' },
        { id: 'w2', name: 'Validación de alertas críticas', state: 'running', last_run: '2026-05-22 10:05' },
        { id: 'w3', name: 'Optimización rutas', state: 'idle', last_run: '2026-05-20 17:30' },
    ],
}

export const mockAdminUsers = [
    { id: 1, nombre_completo: 'Ana Torres', correo: 'ana.torres@example.com', role: 'admin', is_active: true },
    { id: 2, nombre_completo: 'Carlos Vega', correo: 'carlos.vega@example.com', role: 'manager', is_active: true },
    { id: 3, nombre_completo: 'Paula Jiménez', correo: 'paula.jimenez@example.com', role: 'viewer', is_active: false },
]
