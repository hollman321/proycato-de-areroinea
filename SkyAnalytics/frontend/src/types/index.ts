// Auth types
export interface User {
    id: number
    email: string
    full_name: string | null
    role: string
    is_active: boolean
    genero?: string
    numero_celular?: string
    fecha_nacimiento?: string
    foto_perfil?: string
    estado_usuario?: string
    cantidad_viajes?: number
    total_gastado?: number
    descuento_actual?: string
}

export interface LoginRequest {
    email: string
    password: string
}

export interface RegisterRequest {
    email: string
    password: string
    full_name?: string
}

export interface AuthResponse {
    access_token: string
    token_type: string
    user: User
}

// Dashboard types
export interface DashboardStats {
    usuarios_activos: number
    viajes_completados: number
    viajes_cancelados: number
    ingresos: number
    clientes_frecuentes: number
    tiempo_promedio: number
    rutas_populares: string[]
    pais_mas_activo: string
}

export interface ChartData {
    name: string
    value: number
    [key: string]: any
}

// Filters
export interface DashboardFilters {
    pais?: string
    ciudad?: string
    fecha_desde?: string
    fecha_hasta?: string
    usuario?: string
    genero?: string
    tipo_recorrido?: string
    viajes_frecuentes?: boolean
    nombre?: string
    correo?: string
}

// API Response types
export interface ApiResponse<T> {
    data: T
    message?: string
}

export interface PaginatedResponse<T> {
    data: T[]
    total: number
    page: number
    limit: number
    totalPages: number
}