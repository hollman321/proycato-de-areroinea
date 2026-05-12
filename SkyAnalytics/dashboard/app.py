"""
SkyAnalytics — consola analítica tipo SaaS (Streamlit).

Flujo:
1) Tema y layout (sidebar + topbar).
2) Si no hay JWT válido en sesión → pantalla de login / registro.
3) Con token → páginas que consumen FastAPI (`/analytics/*`, `/pasajeros`, etc.).

Los KPIs y tablas pesadas usan la API con paginación por cursor para escalar a millones de filas.
"""

from __future__ import annotations

import io
import os
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import bindparam, create_engine, text

from api_client import ApiError, api_get_json, api_login, api_me, api_register
from theme import build_css

# -----------------------------------------------------------------------------
# Configuración de página Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SkyAnalytics",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:secretpassword@localhost:5432/skyanalytics",
)


def _init_session() -> None:
    defaults: Dict[str, Any] = {
        "authenticated": False,
        "token": None,
        "user": None,
        "nav": "Dashboard",
        "dark_theme": True,
        "table_cursor": None,
        "api_online": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_session()

st.markdown(build_css(dark=bool(st.session_state.dark_theme)), unsafe_allow_html=True)


def system_online() -> bool:
    """Ping rápido al backend para el indicador online/offline en la topbar."""
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


@st.cache_resource
def get_db_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)


def render_topbar() -> None:
    st.session_state.api_online = system_online()
    online_cls = "pill-live" if st.session_state.api_online else "pill-offline"
    online_txt = "API online" if st.session_state.api_online else "API offline"
    user = st.session_state.user or {}
    label = user.get("email", "Usuario")
    st.markdown(
        f"""
        <div class="topbar glass">
          <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap;">
            <span class="pill {online_cls}"><span class="fa-solid fa-signal"></span> {online_txt}</span>
            <span class="pill"><span class="fa-solid fa-database"></span> PostgreSQL</span>
          </div>
          <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap;">
            <span class="pill"><span class="fa-solid fa-user"></span> {label}</span>
            <span class="pill"><span class="fa-regular fa-bell"></span> Notificaciones</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login() -> None:
    st.markdown(
        """
        <div class="auth-card">
          <div class="auth-brand">SkyAnalytics</div>
          <div class="auth-sub">Analítica de pasajeros con experiencia SaaS empresarial.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_register = st.tabs(["Iniciar sesión", "Crear cuenta"])

    with tab_login:
        show_pw = st.checkbox("Mostrar contraseña", value=False)
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="admin@skyanalytics.com")
            password = st.text_input("Contraseña", type="password" if not show_pw else "default")
            remember = st.checkbox("Recordarme en este equipo", value=True)
            submitted = st.form_submit_button("Entrar")
        if submitted:
            try:
                token = api_login(API_BASE_URL, email, password, remember_me=remember)
                st.session_state.token = token
                st.session_state.user = api_me(API_BASE_URL, token)
                st.session_state.authenticated = True
                try:
                    st.toast("Bienvenido", icon="✅")
                except Exception:
                    pass
                st.rerun()
            except ApiError as e:
                st.error(str(e))

        with st.expander("¿Olvidaste tu contraseña?"):
            st.caption(
                "Introduce tu email; si existe en el sistema recibirás instrucciones (flujo simulado vía API)."
            )
            fp_email = st.text_input("Email de recuperación", key="fp_email")
            if st.button("Enviar enlace", key="fp_send"):
                try:
                    r = requests.post(
                        f"{API_BASE_URL}/auth/forgot-password",
                        json={"email": fp_email},
                        timeout=15,
                    )
                    msg = r.json().get("message", "Solicitud registrada.") if r.status_code == 200 else r.text
                    st.success(msg)
                except Exception as ex:
                    st.warning(f"No se pudo contactar la API: {ex}")

    with tab_register:
        with st.form("register_form"):
            re_email = st.text_input("Email (registro)", key="re_email")
            re_name = st.text_input("Nombre completo (opcional)", key="re_name")
            re_pw = st.text_input("Contraseña (mín. 8 caracteres)", type="password", key="re_pw")
            re_go = st.form_submit_button("Registrarme")
        if re_go:
            try:
                api_register(API_BASE_URL, re_email, re_pw, re_name or None)
                st.success("Cuenta creada. Ahora inicia sesión en la pestaña anterior.")
            except ApiError as e:
                st.error(str(e))


def logout() -> None:
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user = None
    try:
        st.toast("Sesión cerrada", icon="👋")
    except Exception:
        pass
    st.rerun()


def _auth_headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {st.session_state.token}"}


def page_dashboard() -> None:
    token = st.session_state.token
    res = api_get_json(API_BASE_URL, token, "/analytics/resumen")
    paises = api_get_json(API_BASE_URL, token, "/analytics/por-pais", {"limit": 15})
    tend = api_get_json(API_BASE_URL, token, "/analytics/tendencia-mensual")

    ttl = res.get("cache_ttl_seconds", 30)
    dias = res.get("cobertura_activa_dias", 30)
    hist_paises = res.get("paises_historico_distintos", 0)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="kpi"><div class="kpi-label">Volumen total</div><div class="kpi-value">{res["total_pasajeros"]:,}</div>'
            f'<div class="kpi-caption">Registros en base operativa</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="kpi"><div class="kpi-label">Países (cobertura activa)</div>'
            f'<div class="kpi-value">{res["paises_cobertura_activa_30d"]:,}</div>'
            f'<div class="kpi-caption">≥1 pasajero en últimos {dias} días · histórico: {hist_paises:,} países</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="kpi"><div class="kpi-label">Ciudades (nodos)</div>'
            f'<div class="kpi-value">{res["ciudades_nodos_urbanos"]:,}</div>'
            f'<div class="kpi-caption">Ciudades distintas con actividad</div></div>',
            unsafe_allow_html=True,
        )
    st.caption(
        f"SkyAnalytics Operational Intelligence — KPIs con caché de API {ttl}s (no fuerces refrescos más rápidos en el cliente)."
    )

    st.markdown('<div class="section-title">Distribución y tendencia</div>', unsafe_allow_html=True)
    df_p = pd.DataFrame(paises)
    df_t = pd.DataFrame(tend)
    col_a, col_b = st.columns(2)
    with col_a:
        if not df_p.empty:
            fig = px.bar(
                df_p,
                x="cantidad",
                y="pais",
                orientation="h",
                color="cantidad",
                color_continuous_scale=["#0ea5e9", "#6366f1", "#f59e0b"],
            )
            fig.update_layout(
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=8, r=8, t=28, b=8),
                title="Top países",
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with col_b:
        if not df_t.empty:
            fig2 = px.line(df_t, x="mes", y="cantidad", markers=True)
            fig2.update_traces(line=dict(width=3))
            fig2.update_layout(
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=8, r=8, t=28, b=8),
                title="Registros mensuales",
            )
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})


def page_pasajeros() -> None:
    token = st.session_state.token
    st.markdown('<div class="section-title">Exploración con cursor (alto volumen)</div>', unsafe_allow_html=True)
    q = st.text_input("Búsqueda en tiempo real (nombre o correo)", value="", key="pq")
    if st.session_state.get("_prev_pq", "") != q.strip():
        st.session_state.table_cursor = None
    st.session_state._prev_pq = q.strip()
    limit = st.slider("Filas por página", 25, 500, 100, 25)

    params: Dict[str, Any] = {"limit": limit}
    if q.strip():
        params["q"] = q.strip()
    if st.session_state.table_cursor is not None:
        params["cursor"] = int(st.session_state.table_cursor)

    data = api_get_json(API_BASE_URL, token, "/analytics/pasajeros", params)
    items = data.get("items", [])
    df = pd.DataFrame(items)
    st.caption(f"Mostrando {len(df)} filas · has_more={data.get('has_more')} · next_cursor={data.get('next_cursor')}")
    st.dataframe(df, use_container_width=True, height=420)

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Página siguiente"):
            if data.get("next_cursor"):
                st.session_state.table_cursor = data["next_cursor"]
                st.rerun()
    with b2:
        if st.button("Reiniciar cursor"):
            st.session_state.table_cursor = None
            st.rerun()
    with b3:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Exportar CSV (página actual)", csv, "pasajeros_pagina.csv", "text/csv")

    try:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="pasajeros")
        buf.seek(0)
        st.download_button(
            "Exportar Excel (página actual)",
            buf.getvalue(),
            "pasajeros_pagina.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception:
        st.info("Instala openpyxl en el contenedor dashboard para exportar Excel.")


def page_reportes() -> None:
    token = st.session_state.token
    st.markdown('<div class="section-title">Reportes ejecutivos</div>', unsafe_allow_html=True)
    cat = api_get_json(API_BASE_URL, token, "/estadisticas/categorias")
    st.json(cat)


def page_config() -> None:
    st.markdown('<div class="section-title">Preferencias</div>', unsafe_allow_html=True)
    dark = st.toggle("Modo oscuro", value=st.session_state.dark_theme)
    if dark != st.session_state.dark_theme:
        st.session_state.dark_theme = dark
        st.rerun()
    st.text_input("API_BASE_URL (solo lectura en UI)", value=API_BASE_URL, disabled=True)
    if st.button("Cerrar sesión", type="primary"):
        logout()


def page_analytics() -> None:
    """Vista enfocada en series; reutiliza datos del dashboard con filtros simples."""
    st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)
    page_dashboard()


# -----------------------------------------------------------------------------
# Auth gate
# -----------------------------------------------------------------------------
if not st.session_state.authenticated:
    render_login()
    st.stop()

# -----------------------------------------------------------------------------
# Layout autenticado: sidebar + contenido
# -----------------------------------------------------------------------------
filtro_paises: List[str] = []
with st.sidebar:
    st.markdown("### Navegación")
    nav = st.radio(
        "Sección",
        ["Dashboard", "Analytics", "Pasajeros", "Reportes", "Configuración"],
        label_visibility="collapsed",
    )
    st.session_state.nav = nav
    st.markdown("---")
    st.caption("Filtros locales (consulta directa opcional a PostgreSQL para listados cortos).")
    engine = get_db_engine()
    try:
        paises_df = pd.read_sql("SELECT DISTINCT pais FROM pasajeros ORDER BY pais", engine)
        filtro_paises = st.multiselect("País (SQL opcional)", options=paises_df["pais"].tolist())
    except Exception:
        st.warning("No se pudo leer la lista de países desde PostgreSQL (revisa DATABASE_URL).")

render_topbar()

if st.session_state.nav == "Dashboard":
    page_dashboard()
elif st.session_state.nav == "Analytics":
    page_analytics()
elif st.session_state.nav == "Pasajeros":
    page_pasajeros()
elif st.session_state.nav == "Reportes":
    page_reportes()
else:
    page_config()

# Opcional: bloque SQL ligero para usuarios que quieren cruzar filtros de sidebar sin pasar por la API
if filtro_paises and st.session_state.nav == "Dashboard":
    st.markdown('<div class="section-title">Vista cruzada (muestra limitada)</div>', unsafe_allow_html=True)
    engine = get_db_engine()
    sql = "SELECT * FROM pasajeros WHERE pais IN :p LIMIT 500"
    t = text(sql).bindparams(bindparam("p", expanding=True))
    try:
        with engine.connect() as conn:
            dfx = pd.read_sql(t, conn, params={"p": list(filtro_paises)})
        st.dataframe(dfx, use_container_width=True, height=320)
    except Exception as ex:
        st.warning(f"No se pudo ejecutar la consulta opcional: {ex}")
