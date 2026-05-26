/**
 * API Handler para los endpoints de IA
 * Redirige las llamadas del frontend al backend
 */

// Este archivo es opcional si usas el cliente Axios directamente
// Pero puede ser útil para agregar lógica adicional del lado del cliente

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export const AI_ENDPOINTS = {
    GREETING: '/ai/greeting',
    CHAT: '/ai/chat',
    CONTEXT: '/ai/context',
    HELP: '/ai/help',
    HISTORY: '/ai/history',
    CLEAR_HISTORY: '/ai/clear-history',
    MODULES: '/ai/modules',
    QUICK_LINKS: (module: string) => `/ai/quick-links/${module}`,
};

export function getAIEndpoint(endpoint: string): string {
    return `${API_BASE_URL}${endpoint}`;
}
