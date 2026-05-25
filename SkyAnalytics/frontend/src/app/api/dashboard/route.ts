import { NextResponse } from 'next/server'
import prisma from '@/lib/prisma'
import bcrypt from 'bcryptjs'

export async function POST(request: Request) {
    try {
        const { email, password, full_name } = await request.json()

        if (!email || !password) {
            return NextResponse.json({ error: 'Email y contraseña requeridos' }, { status: 400 })
        }

        // Verificar si el usuario ya existe
        const existingUser = await prisma.user.findUnique({ where: { email } })
        if (existingUser) {
            return NextResponse.json({ error: 'El usuario ya existe' }, { status: 400 })
        }

        // Hash de contraseña
        const hashedPassword = await bcrypt.hash(password, 12)

        // Crear usuario con rol por defecto OPERATOR
        const user = await prisma.user.create({
            data: {
                email,
                password: hashedPassword,
                full_name,
                role: 'OPERATOR'
            },
            select: {
                id: true,
                email: true,
                full_name: true,
                role: true
            }
        })

        return NextResponse.json(user)
    } catch (error) {
        return NextResponse.json({ error: 'Error al registrar usuario' }, { status: 500 })
    }
}
