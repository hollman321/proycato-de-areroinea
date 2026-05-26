/**
 * Servicio de API para el módulo de IA
 * Comunicación con los endpoints /ai/* del backend
 */

import { api } from './api';

interface ChatMessage {
    message: string;
    route?: string;
    user_id?: number;
}

interface ChatResponse {
    message: string;
    intent: string;
    suggestions?: string[];
    quick_tips?: string[];
    module_info?: Record<string, unknown>;
}

interface ContextResponse {
    module: string;
    description: string;
    features: string[];
    actions: string[];
    tips: string[];
    contextual_help: string;
}

interface HelpResponse extends ChatResponse { }

interface GreetingResponse {
    greeting: string;
    suggestions: string[];
}

interface HistoryMessage {
    timestamp: string;
    is_user: boolean;
    message: string;
    intent?: string;
}

interface HistoryResponse {
    conversation: HistoryMessage[];
    total_messages: number;
}

export const iaService = {
    /**
     * Obtiene un saludo inicial del asistente IA
     */
    async getGreeting(): Promise<GreetingResponse> {
        try {
            const response = await api.get('/ai/greeting');
            return response.data;
        } catch (error) {
            console.error('Error getting greeting:', error);
            throw error;
        }
    },

    /**
     * Envía un mensaje al chatbot IA
     */
    async sendMessage(message: string, route?: string): Promise<ChatResponse> {
        try {
            const payload: ChatMessage = {
                message,
                route: route || window.location.pathname,
            };

            const response = await api.post('/ai/chat', payload);
            return response.data;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    },

    /**
     * Obtiene contexto del módulo actual
     */
    async getContext(route: string): Promise<ContextResponse> {
        try {
            const response = await api.post('/ai/context', {
                route: route || window.location.pathname,
            });
            return response.data;
        } catch (error) {
            console.error('Error getting context:', error);
            throw error;
        }
    },

    /**
     * Obtiene ayuda específica para una pregunta
     */
    async getHelp(question: string, route?: string): Promise<HelpResponse> {
        try {
            const response = await api.post('/ai/help', {
                question,
                route: route || window.location.pathname,
            });
            return response.data;
        } catch (error) {
            console.error('Error getting help:', error);
            throw error;
        }
    },

    /**
     * Obtiene el historial de conversación
     */
    async getHistory(limit: number = 10): Promise<HistoryResponse> {
        try {
            const response = await api.get('/ai/history', {
                params: { limit },
            });
            return response.data;
        } catch (error) {
            console.error('Error getting history:', error);
            throw error;
        }
    },

    /**
     * Limpia el historial de conversación
     */
    async clearHistory(): Promise<{ success: boolean; message: string }> {
        try {
            const response = await api.post('/ai/clear-history', {});
            return response.data;
        } catch (error) {
            console.error('Error clearing history:', error);
            throw error;
        }
    },

    /**
     * Obtiene información de todos los módulos disponibles
     */
    async getAllModules(): Promise<{
        modules: Record<string, { title: string; description: string; actions_count: number; features_count: number }>;
        total: number;
    }> {
        try {
            const response = await api.get('/ai/modules');
            return response.data;
        } catch (error) {
            console.error('Error getting modules:', error);
            throw error;
        }
    },

    /**
     * Obtiene links rápidos para un módulo específico
     */
    async getQuickLinks(module: string): Promise<{
        module: string;
        links: Array<{ label: string; icon?: string }>;
    }> {
        try {
            const response = await api.get(`/ai/quick-links/${module}`);
            return response.data;
        } catch (error) {
            console.error('Error getting quick links:', error);
            throw error;
        }
    },
};
