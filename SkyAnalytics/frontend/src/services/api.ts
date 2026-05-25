import axios, { AxiosRequestConfig } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('auth-token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            if (typeof window !== 'undefined') {
                localStorage.removeItem('auth-token')
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export async function getWithFallback<T>(path: string, fallback: T, config?: AxiosRequestConfig): Promise<T> {
    try {
        const response = await api.get<T>(path, config)
        return response.data
    } catch {
        return fallback
    }
}

export async function postWithFallback<T>(path: string, payload: any, fallback: T, config?: AxiosRequestConfig): Promise<T> {
    try {
        const response = await api.post<T>(path, payload, config)
        return response.data
    } catch {
        return fallback
    }
}

export async function putWithFallback<T>(path: string, payload: any, fallback: T, config?: AxiosRequestConfig): Promise<T> {
    try {
        const response = await api.put<T>(path, payload, config)
        return response.data
    } catch {
        return fallback
    }
}

export async function deleteWithFallback<T>(path: string, fallback: T, config?: AxiosRequestConfig): Promise<T> {
    try {
        const response = await api.delete<T>(path, config)
        return response.data
    } catch {
        return fallback
    }
}

export default api