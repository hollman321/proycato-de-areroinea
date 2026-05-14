import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
    const token = request.cookies.get('auth-token')?.value

    // Protected routes
    const protectedRoutes = ['/dashboard', '/users', '/maps', '/settings']
    const isProtectedRoute = protectedRoutes.some(route =>
        request.nextUrl.pathname.startsWith(route)
    )

    // Auth routes
    const authRoutes = ['/login', '/register', '/forgot-password']
    const isAuthRoute = authRoutes.some(route =>
        request.nextUrl.pathname.startsWith(route)
    )

    if (isProtectedRoute && !token) {
        return NextResponse.redirect(new URL('/login', request.url))
    }

    if (isAuthRoute && token) {
        return NextResponse.redirect(new URL('/dashboard', request.url))
    }

    return NextResponse.next()
}

export const config = {
    matcher: [
        '/dashboard/:path*',
        '/users/:path*',
        '/maps/:path*',
        '/settings/:path*',
        '/login',
        '/register',
        '/forgot-password',
    ],
}