import { NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

type RouteContext = {
    params: Promise<{ id: string }>
}

export async function PATCH(request: Request, { params }: RouteContext) {
    try {
        const { id: routeId } = await params
        const body = await request.json()
        const { id, createdAt, updatedAt, ...updateData } = body

        if (updateData.amount) updateData.amount = parseFloat(updateData.amount)
        if (updateData.date) updateData.date = new Date(updateData.date)

        const transaction = await prisma.transaction.update({
            where: { id: routeId },
            data: updateData,
        })
        return NextResponse.json(transaction)
    } catch (error) {
        console.error('Error in Finance PATCH:', error)
        return NextResponse.json({ error: 'Error al actualizar transacción' }, { status: 500 })
    }
}

export async function DELETE(request: Request, { params }: RouteContext) {
    try {
        const { id } = await params

        await prisma.transaction.delete({
            where: { id },
        })
        return NextResponse.json({ message: 'Transacción eliminada' })
    } catch (error) {
        console.error('Error in Finance DELETE:', error)
        return NextResponse.json({ error: 'Error al eliminar transacción' }, { status: 500 })
    }
}
