'use client';

import { useState, useCallback, useRef } from 'react';
import { iaService } from '@/services/ia';

export interface Message {
    id: string;
    content: string;
    isUser: boolean;
    timestamp: Date;
    intent?: string;
    suggestions?: string[];
    quickTips?: string[];
}

export function useChatIA(initialRoute: string = '/dashboard') {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [currentRoute, setCurrentRoute] = useState(initialRoute);
    const conversationIdRef = useRef<string>(Date.now().toString());

    /**
     * Cargar saludo inicial
     */
    const loadGreeting = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            const greeting = await iaService.getGreeting();

            const message: Message = {
                id: Date.now().toString(),
                content: greeting.greeting,
                isUser: false,
                timestamp: new Date(),
                suggestions: greeting.suggestions,
            };

            setMessages([message]);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Error loading greeting';
            setError(errorMessage);
            console.error('Error loading greeting:', err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    /**
     * Enviar mensaje al chatbot IA
     */
    const sendMessage = useCallback(
        async (text: string) => {
            if (!text.trim()) return;

            // Agregar mensaje del usuario
            const userMessage: Message = {
                id: (Date.now()).toString(),
                content: text,
                isUser: true,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, userMessage]);
            setIsLoading(true);
            setError(null);

            try {
                const response = await iaService.sendMessage(text, currentRoute);

                const aiMessage: Message = {
                    id: (Date.now() + 1).toString(),
                    content: response.message,
                    isUser: false,
                    timestamp: new Date(),
                    intent: response.intent,
                    suggestions: response.suggestions,
                    quickTips: response.quick_tips,
                };

                setMessages((prev) => [...prev, aiMessage]);
            } catch (err) {
                const errorMessage = err instanceof Error ? err.message : 'Error sending message';
                setError(errorMessage);

                const errorAIMessage: Message = {
                    id: (Date.now() + 2).toString(),
                    content: 'Disculpa, ocurrió un error. Por favor intenta de nuevo.',
                    isUser: false,
                    timestamp: new Date(),
                };

                setMessages((prev) => [...prev, errorAIMessage]);
                console.error('Error sending message:', err);
            } finally {
                setIsLoading(false);
            }
        },
        [currentRoute]
    );

    /**
     * Obtener contexto del módulo actual
     */
    const getModuleContext = useCallback(async (route?: string) => {
        const moduleRoute = route || currentRoute;

        try {
            const context = await iaService.getContext(moduleRoute);
            return context;
        } catch (err) {
            console.error('Error getting context:', err);
            throw err;
        }
    }, [currentRoute]);

    /**
     * Obtener ayuda para una pregunta específica
     */
    const getHelp = useCallback(
        async (question: string) => {
            try {
                const help = await iaService.getHelp(question, currentRoute);
                return help;
            } catch (err) {
                console.error('Error getting help:', err);
                throw err;
            }
        },
        [currentRoute]
    );

    /**
     * Obtener historial de conversación
     */
    const getHistory = useCallback(async (limit: number = 10) => {
        try {
            const history = await iaService.getHistory(limit);
            return history;
        } catch (err) {
            console.error('Error getting history:', err);
            throw err;
        }
    }, []);

    /**
     * Limpiar historial
     */
    const clearHistory = useCallback(async () => {
        try {
            await iaService.clearHistory();
            setMessages([]);
        } catch (err) {
            console.error('Error clearing history:', err);
            throw err;
        }
    }, []);

    /**
     * Actualizar ruta actual
     */
    const updateRoute = useCallback((newRoute: string) => {
        setCurrentRoute(newRoute);
    }, []);

    /**
     * Limpiar mensajes
     */
    const clearMessages = useCallback(() => {
        setMessages([]);
    }, []);

    /**
     * Obtener último mensaje
     */
    const getLastMessage = useCallback((): Message | undefined => {
        return messages[messages.length - 1];
    }, [messages]);

    /**
     * Obtener sugerencias del último mensaje IA
     */
    const getLastSuggestions = useCallback((): string[] | undefined => {
        const lastMessage = getLastMessage();
        return lastMessage && !lastMessage.isUser ? lastMessage.suggestions : undefined;
    }, [getLastMessage]);

    return {
        // Estado
        messages,
        isLoading,
        error,
        currentRoute,

        // Métodos
        loadGreeting,
        sendMessage,
        getModuleContext,
        getHelp,
        getHistory,
        clearHistory,
        updateRoute,
        clearMessages,
        getLastMessage,
        getLastSuggestions,

        // Utilidades
        conversationId: conversationIdRef.current,
    };
}
