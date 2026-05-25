import { NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

type RouteContext = {
    params: Promise<{ id: string }>
}

export async function PATCH(request: Request, { params }: RouteContext) {
    try {
        const { id: routeId } = await params
        const body = await request.json()
        const { id, createdAt, updatedAt, client, operator, ...updateData } = body

        const operation = await prisma.operation.update({
            where: { id: routeId },
            data: updateData,
        })
        return NextResponse.json(operation)
    } catch {
        return NextResponse.json({ error: 'Error al actualizar operación' }, { status: 500 })
    }
}

export async function DELETE(request: Request, { params }: RouteContext) {
    try {
        const { id } = await params

        await prisma.operation.delete({
            where: { id },
        })
        return NextResponse.json({ message: 'Operación eliminada' })
    } catch {
        return NextResponse.json({ error: 'Error al eliminar operación' }, { status: 500 })
    }
}
