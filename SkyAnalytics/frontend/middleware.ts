import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Rutas sensibles y sus requisitos
const ADMIN_PREFIX = '/admin';
const PRIVATE_ROUTES = ['/dashboard', '/profile', '/users'];

export function middleware(request: NextRequest) {
    const token = request.cookies.get('auth_token')?.value;
    const userRole = request.cookies.get('user_role')?.value;
    const { pathname } = request.nextUrl;

    // 1. Protección de rutas administrativas
    const isPathsAdmin = pathname.startsWith(ADMIN_PREFIX) || pathname.startsWith('/users') || pathname.startsWith('/settings/admin');

    if (isPathsAdmin) {
        if (!token) return NextResponse.redirect(new URL('/login', request.url));

        if (userRole !== 'ADMIN' && userRole !== 'SUPERADMIN') {
            const url = request.nextUrl.clone();
            url.pathname = '/unauthorized';
            return NextResponse.redirect(url);
        }
    }

    // 2. Protección de rutas privadas generales
    if (PRIVATE_ROUTES.some(route => pathname.startsWith(route)) && !token) {
        return NextResponse.redirect(new URL('/login', request.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/admin/:path*', '/dashboard/:path*', '/profile/:path*', '/users/:path*'],
};