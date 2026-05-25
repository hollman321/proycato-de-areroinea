import { NextResponse } from 'next/server'

export async function GET() {
    const apiUrl = process.env.API_URL
    const apiToken = process.env.API_TOKEN

    if (!apiUrl || !apiToken || apiToken === 'tu_token_aqui') {
        return NextResponse.json(
            { error: 'Configura API_URL y API_TOKEN en el archivo .env' },
            { status: 500 }
        )
    }

    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                Accept: 'application/json',
                Authorization: `Bearer ${apiToken}`,
            },
            cache: 'no-store',
        })

        const contentType = response.headers.get('content-type') || ''
        const body = contentType.includes('application/json')
            ? await response.json()
            : await response.text()

        if (!response.ok) {
            return NextResponse.json(
                {
                    error: 'Error al autenticar con la API externa',
                    status: response.status,
                    detail: body,
                },
                { status: response.status }
            )
        }

        return NextResponse.json(body)
    } catch {
        return NextResponse.json(
            { error: 'No se pudo conectar con la API externa' },
            { status: 500 }
        )
    }
}
