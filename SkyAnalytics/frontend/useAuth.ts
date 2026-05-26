'use client';
import { useState, useEffect } from 'react';
import { getCookie } from 'cookies-next'; // Asumiendo esta librería común o usar document.cookie
import { useAuthStore } from '@/store/auth';

export const useAuth = () => {
    const { user: storeUser, isAuthenticated: storeAuth } = useAuthStore();
    const [isLoading, setIsLoading] = useState(true);
    const [sessionUser, setSessionUser] = useState(storeUser);

    useEffect(() => {
        const checkAuth = () => {
            try {
                const token = getCookie('auth_token');

                if (token && storeAuth) {
                    setSessionUser(storeUser);
                } else {
                    setSessionUser(null);
                    // Podríamos disparar un re-fetch del perfil aquí si el token existe pero el store está vacío
                }
            } catch (error) {
                console.error("Auth check failed", error);
                setSessionUser(null);
            } finally {
                setIsLoading(false);
            }
        };

        checkAuth();
    }, [storeUser, storeAuth]);

    return { user: sessionUser, isLoading, isAuthenticated: !!sessionUser };
};