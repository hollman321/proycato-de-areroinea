import { NextResponse } from "next/server";
import { z } from "zod";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
});

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, password } = loginSchema.parse(body);

    // Autenticar contra el backend FastAPI
    const backendResponse = await fetch(`${BACKEND_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email,
        password,
        remember_me: false,
      }),
    });

    if (!backendResponse.ok) {
      return NextResponse.json(
        { error: "Correo o contraseña incorrectos." },
        { status: 401 },
      );
    }

    const backendData = await backendResponse.json();
    const token = backendData.access_token;

    // Obtener datos del usuario del backend
    const userResponse = await fetch(`${BACKEND_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!userResponse.ok) {
      return NextResponse.json(
        { error: "Error al obtener datos del usuario." },
        { status: 500 },
      );
    }

    const user = await userResponse.json();

    const response = NextResponse.json({
      data: {
        user: {
          id: user.id,
          email: user.email,
          full_name: user.full_name,
          role: user.role,
        },
        token,
      },
    });

    response.cookies.set("auth-token", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60 * 24 * 30,
    });
    response.cookies.set("user-role", user.role, {
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60 * 24 * 30,
    });

    return response;
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({ error: error.errors }, { status: 400 });
    }
    return NextResponse.json(
      { error: "Error interno durante el login." },
      { status: 500 },
    );
  }
}
