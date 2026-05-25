const API_URL = "/api/external-data";

export async function obtenerDatos() {
  try {
    const response = await fetch(API_URL);

    if (!response.ok) {
      const error = await response.json().catch(() => null);
      throw new Error(error?.error || "Error de autenticacion");
    }

    const data = await response.json();

    return data;
  } catch (error) {
    console.error(error);
  }
}
