import axios, { AxiosRequestConfig } from "axios";
import { deleteCookie, getCookie } from "cookies-next";
import { v4 as uuidv4 } from "uuid";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://localhost:8001";

console.log("API_BASE_URL:", API_BASE_URL);

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

const getAuthToken = () => {
  if (typeof window === "undefined") {
    return null;
  }
  // Intentar obtener del localStorage primero, luego de cookies
  const localToken = localStorage.getItem("auth-token");
  if (localToken) return localToken;

  const cookieToken = getCookie("auth-token");
  return cookieToken || null;
};

api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    config.headers = config.headers ?? {};
    // Inyectar Correlation ID para tracing distribuido
    config.headers["X-Correlation-ID"] = uuidv4();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      (error.response?.status === 401 || error.response?.status === 403) &&
      typeof window !== "undefined"
    ) {
      deleteCookie("auth-token");

      if (error.response?.status === 403) {
        window.location.href = "/unauthorized";
      } else if (!window.location.pathname.includes("/login")) {
        window.location.href = "/login?expired=true";
      }
    }
    const message =
      error.response?.data?.error ||
      error.message ||
      "Error interno del servidor";
    return Promise.reject(new Error(message));
  },
);

export async function getWithFallback<T>(
  path: string,
  fallback: T,
  config?: AxiosRequestConfig,
): Promise<T> {
  try {
    const response = await api.get<T>(path, config);
    return response.data;
  } catch {
    return fallback;
  }
}

export async function postWithFallback<T>(
  path: string,
  payload: unknown,
  fallback: T,
  config?: AxiosRequestConfig,
): Promise<T> {
  try {
    const response = await api.post<T>(path, payload, config);
    return response.data;
  } catch {
    return fallback;
  }
}

export async function putWithFallback<T>(
  path: string,
  payload: unknown,
  fallback: T,
  config?: AxiosRequestConfig,
): Promise<T> {
  try {
    const response = await api.put<T>(path, payload, config);
    return response.data;
  } catch {
    return fallback;
  }
}

export async function deleteWithFallback<T>(
  path: string,
  fallback: T,
  config?: AxiosRequestConfig,
): Promise<T> {
  try {
    const response = await api.delete<T>(path, config);
    return response.data;
  } catch {
    return fallback;
  }
}

export default api;
