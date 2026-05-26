'use client';

import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface RoleGuardProps {
    children: React.ReactNode;
    allowedRoles: string[];
    fallback?: React.ReactNode;
}

export const RoleGuard = ({ children, allowedRoles, fallback = null }: RoleGuardProps) => {
    const { user, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && (!user || !allowedRoles.includes(user.role))) {
            // Solo redirigir si el usuario no tiene acceso a la página completa
            // Si es un componente parcial, el fallback se encargará
            const isCriticalPath = window.location.pathname.startsWith('/admin') ||
                window.location.pathname.startsWith('/users');

            if (isCriticalPath) {
                router.push('/unauthorized');
            }
        }
    }, [user, isLoading, allowedRoles, router]);

    if (isLoading) return null; // O un Skeleton loader profesional

    if (!user || !allowedRoles.includes(user.role)) {
        return <>{fallback}</>;
    }

    return <>{children}</>;
};