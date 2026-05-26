'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { MessageCircle, X, Send, Loader } from 'lucide-react';

interface ChatMessage {
    id: string;
    content: string;
    isUser: boolean;
    timestamp: Date;
    intent?: string;
    suggestions?: string[];
    quickTips?: string[];
}

interface ChatIAProps {
    currentRoute?: string;
}

export function ChatIA({ currentRoute = '/dashboard' }: ChatIAProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showSuggestions, setShowSuggestions] = useState(true);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const router = useRouter();

    // Scroll automático al último mensaje
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Cargar saludo inicial
    useEffect(() => {
        if (isOpen && messages.length === 0) {
            loadGreeting();
        }
    }, [isOpen]);

    const loadGreeting = async () => {
        try {
            setIsLoading(true);
            const response = await fetch('/api/ai/greeting');
            const data = await response.json();

            const greeting: ChatMessage = {
                id: Date.now().toString(),
                content: data.greeting,
                isUser: false,
                timestamp: new Date(),
                suggestions: data.suggestions,
            };

            setMessages([greeting]);
            setShowSuggestions(true);
        } catch (error) {
            console.error('Error loading greeting:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSendMessage = async (message?: string) => {
        const textToSend = message || inputValue.trim();

        if (!textToSend) return;

        // Agregar mensaje del usuario
        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            content: textToSend,
            isUser: true,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInputValue('');
        setShowSuggestions(false);
        setIsLoading(true);

        try {
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: textToSend,
                    route: currentRoute,
                }),
            });

            const data = await response.json();

            const aiMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                content: data.message,
                isUser: false,
                timestamp: new Date(),
                intent: data.intent,
                suggestions: data.suggestions,
                quickTips: data.quick_tips,
            };

            setMessages((prev) => [...prev, aiMessage]);
            setShowSuggestions(data.suggestions && data.suggestions.length > 0);
        } catch (error) {
            console.error('Error sending message:', error);

            const errorMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                content: 'Disculpa, hubo un error al procesar tu pregunta. Intenta de nuevo.',
                isUser: false,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const suggestions = messages.length > 0 ? messages[messages.length - 1].suggestions : [];

    return (
        <>
            {/* Botón flotante */}
            <motion.button
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsOpen(!isOpen)}
                className="fixed bottom-6 right-6 z-40 bg-gradient-to-r from-blue-600 to-blue-800 hover:from-blue-700 hover:to-blue-900 text-white rounded-full p-4 shadow-2xl transition-all duration-300"
                aria-label={isOpen ? 'Cerrar chat' : 'Abrir chat IA'}
            >
                <AnimatePresence mode="wait">
                    {isOpen ? (
                        <motion.div
                            key="close"
                            initial={{ rotate: -90, opacity: 0 }}
                            animate={{ rotate: 0, opacity: 1 }}
                            exit={{ rotate: 90, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                        >
                            <X size={24} />
                        </motion.div>
                    ) : (
                        <motion.div
                            key="open"
                            initial={{ rotate: 90, opacity: 0 }}
                            animate={{ rotate: 0, opacity: 1 }}
                            exit={{ rotate: -90, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                        >
                            <MessageCircle size={24} />
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.button>

            {/* Ventana del chat */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.8, y: 20 }}
                        transition={{ duration: 0.3 }}
                        className="fixed bottom-24 right-6 z-50 w-96 bg-slate-900 rounded-2xl shadow-2xl border border-slate-700 overflow-hidden flex flex-col"
                        style={{ maxHeight: '600px' }}
                    >
                        {/* Header */}
                        <div className="bg-gradient-to-r from-blue-600 to-blue-800 px-6 py-4">
                            <h3 className="text-white font-bold text-lg">Asistente IA</h3>
                            <p className="text-blue-100 text-xs">Aquí para ayudarte</p>
                        </div>

                        {/* Mensajes */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            {messages.map((message) => (
                                <motion.div
                                    key={message.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.3 }}
                                    className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-xs px-4 py-2 rounded-lg ${message.isUser
                                                ? 'bg-blue-600 text-white rounded-br-none'
                                                : 'bg-slate-700 text-slate-100 rounded-bl-none'
                                            }`}
                                    >
                                        <p className="text-sm leading-relaxed">{message.content}</p>

                                        {/* Quick Tips */}
                                        {!message.isUser && message.quickTips && message.quickTips.length > 0 && (
                                            <div className="mt-2 pt-2 border-t border-slate-600">
                                                <p className="text-xs font-semibold text-blue-300 mb-1">💡 Tips:</p>
                                                {message.quickTips.map((tip, idx) => (
                                                    <p key={idx} className="text-xs text-slate-300">
                                                        • {tip}
                                                    </p>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            ))}

                            {isLoading && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex justify-start"
                                >
                                    <div className="bg-slate-700 text-slate-100 px-4 py-2 rounded-lg rounded-bl-none">
                                        <div className="flex items-center space-x-2">
                                            <Loader size={16} className="animate-spin" />
                                            <span className="text-sm">Pensando...</span>
                                        </div>
                                    </div>
                                </motion.div>
                            )}

                            <div ref={messagesEndRef} />
                        </div>

                        {/* Sugerencias */}
                        {showSuggestions && suggestions && suggestions.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="px-4 py-2 border-t border-slate-700 space-y-2"
                            >
                                <p className="text-xs font-semibold text-slate-400">Sugerencias:</p>
                                <div className="space-y-1">
                                    {suggestions.slice(0, 2).map((suggestion, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => handleSendMessage(suggestion)}
                                            className="w-full text-left text-xs px-3 py-2 bg-slate-800 hover:bg-slate-700 text-blue-300 hover:text-blue-200 rounded transition-colors truncate"
                                        >
                                            {suggestion}
                                        </button>
                                    ))}
                                </div>
                            </motion.div>
                        )}

                        {/* Input */}
                        <div className="border-t border-slate-700 p-3 bg-slate-800">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyPress={(e) => {
                                        if (e.key === 'Enter' && !isLoading) {
                                            handleSendMessage();
                                        }
                                    }}
                                    placeholder="Escribe tu pregunta..."
                                    disabled={isLoading}
                                    className="flex-1 bg-slate-700 text-white placeholder-slate-400 border border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                                />
                                <button
                                    onClick={() => handleSendMessage()}
                                    disabled={isLoading || !inputValue.trim()}
                                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white rounded-lg p-2 transition-colors"
                                    aria-label="Enviar mensaje"
                                >
                                    <Send size={16} />
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
