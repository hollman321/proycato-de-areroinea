"""Cliente HTTP hacia el backend FastAPI (JWT en cabecera)."""

from __future__ import annotations

from typing import Any, Optional

import requests


class ApiError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


def _headers(token: Optional[str]) -> dict[str, str]:
    h: dict[str, str] = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def api_login(base_url: str, email: str, password: str, remember_me: bool) -> str:
    r = requests.post(
        f"{base_url.rstrip('/')}/auth/login",
        json={"email": email, "password": password, "remember_me": remember_me},
        timeout=15,
    )
    if r.status_code != 200:
        raise ApiError(r.json().get("detail", "Error de autenticación"), r.status_code)
    return r.json()["access_token"]


def api_register(base_url: str, email: str, password: str, full_name: Optional[str]) -> None:
    r = requests.post(
        f"{base_url.rstrip('/')}/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
        timeout=15,
    )
    if r.status_code not in (200, 201):
        raise ApiError(r.json().get("detail", "No se pudo registrar"), r.status_code)


def api_post_json(base_url: str, token: Optional[str], path: str, payload: dict[str, Any]) -> Any:
    r = requests.post(
        f"{base_url.rstrip('/')}{path}",
        headers=_headers(token),
        json=payload,
        timeout=30,
    )
    if r.status_code not in (200, 201, 204):
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise ApiError(str(detail), r.status_code)
    if r.status_code == 204:
        return None
    return r.json()


def api_put_json(base_url: str, token: Optional[str], path: str, payload: dict[str, Any]) -> Any:
    r = requests.put(
        f"{base_url.rstrip('/')}{path}",
        headers=_headers(token),
        json=payload,
        timeout=30,
    )
    if r.status_code not in (200, 204):
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise ApiError(str(detail), r.status_code)
    if r.status_code == 204:
        return None
    return r.json()


def api_delete(base_url: str, token: Optional[str], path: str) -> Any:
    r = requests.delete(
        f"{base_url.rstrip('/')}{path}",
        headers=_headers(token),
        timeout=30,
    )
    if r.status_code not in (200, 204):
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise ApiError(str(detail), r.status_code)
    return None


def api_me(base_url: str, token: str) -> dict[str, Any]:
    r = requests.get(f"{base_url.rstrip('/')}/auth/me", headers=_headers(token), timeout=15)
    if r.status_code != 200:
        raise ApiError(r.json().get("detail", "Sesión inválida"), r.status_code)
    return r.json()


def api_get_json(base_url: str, token: str, path: str, params: dict | None = None) -> Any:
    r = requests.get(
        f"{base_url.rstrip('/')}{path}",
        headers=_headers(token),
        params=params or {},
        timeout=60,
    )
    if r.status_code != 200:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise ApiError(str(detail), r.status_code)
    return r.json()
