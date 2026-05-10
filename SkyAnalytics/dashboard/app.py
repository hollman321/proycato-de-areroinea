import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, bindparam
import os
from dotenv import load_dotenv
import redis

# =========================
# CONFIG STREAMLIT
# =========================

st.set_page_config(
    page_title="SkyAnalytics Dashboard",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILOS
# =========================

def inject_global_styles():
    st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

    <style>
    :root{
        --bg: #f8fafc;
        --surface: #ffffff;
        --surface-muted: #f1f5f9;
        --border: #e2e8f0;
        --border-strong: #cbd5e1;
        --text: #1f5f73;
        --muted: #6f8198;
        --primary: #0e7490;
        --primary-dark: #155e75;
        --warning: #d97706;
        --blue: #2563eb;
        --blue-soft: #eff6ff;
        --shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 22px rgba(15, 23, 42, 0.06);
    }

    *{
        font-family: 'Inter', sans-serif;
        letter-spacing: 0;
    }

    .mono,
    .telemetry-value,
    .status-meta,
    .record-count{
        font-family: 'JetBrains Mono', monospace !important;
    }

    .text-primary{
        color: var(--primary) !important;
    }

    html, body, [data-testid="stAppViewContainer"]{
        background: var(--bg) !important;
        color: var(--text) !important;
    }

    [data-testid="stHeader"]{
        background: rgba(248,250,252,0.94);
        border-bottom: 1px solid var(--border);
        backdrop-filter: blur(14px);
    }

    #MainMenu,
    footer,
    [data-testid="stDecoration"],
    [data-testid="stToolbar"]{
        display: none !important;
        visibility: hidden !important;
    }

    section.main > div{
        padding-top: 1rem;
        max-width: 1280px;
        padding-left: 1.25rem;
        padding-right: 1.25rem;
    }

    [data-testid="stSidebar"]{
        background: var(--surface) !important;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] *{
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] h2{
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        margin-bottom: 0.9rem;
        text-transform: uppercase;
    }

    [data-testid="stSidebar"] label{
        color: var(--muted) !important;
        font-size: 0.74rem !important;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"]{
        border-bottom: 1px solid var(--border);
        margin-bottom: 1rem;
        padding-bottom: 0.35rem;
    }

    .sidebar-callout{
        background: var(--surface-muted);
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--muted);
        font-size: 0.78rem;
        font-weight: 600;
        line-height: 1.45;
        margin-bottom: 1rem;
        padding: 0.8rem;
    }

    .sidebar-callout strong{
        color: var(--text);
        display: block;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        margin-bottom: 0.35rem;
        text-transform: uppercase;
    }

    @keyframes fadeInUp{
        from { opacity: 0; transform: translateY(14px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseLive{
        0% { box-shadow: 0 0 0 0 rgba(16,185,129,0.34); }
        70% { box-shadow: 0 0 0 10px rgba(16,185,129,0); }
        100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
    }

    @keyframes sheen{
        0% { transform: translateX(-120%); }
        45%, 100% { transform: translateX(120%); }
    }

    .operational-header,
    .telemetry-strip,
    .kpi-card,
    .section-header,
    .sidebar-callout{
        animation: fadeInUp 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    .operational-header{
        align-items: center;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        box-shadow: var(--shadow);
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.9rem;
        min-height: 86px;
        overflow: hidden;
        padding: 1rem 1.15rem;
        position: relative;
        transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease;
    }

    .operational-header:before{
        background: linear-gradient(180deg, var(--primary), var(--warning));
        content: "";
        height: 100%;
        left: 0;
        position: absolute;
        top: 0;
        width: 3px;
    }

    .operational-header:after{
        background: linear-gradient(90deg, transparent, rgba(14,116,144,0.08), transparent);
        content: "";
        height: 100%;
        left: 0;
        position: absolute;
        top: 0;
        transform: translateX(-120%);
        width: 45%;
        animation: sheen 5.5s ease-in-out infinite;
        pointer-events: none;
    }

    .operational-header:hover{
        border-color: var(--border-strong);
        box-shadow: 0 18px 35px -24px rgba(15,23,42,0.32);
        transform: translateY(-2px);
    }

    .brand-icon{
        align-items: center;
        background: #f8fafc;
        border: 1px solid var(--border);
        border-radius: 10px;
        color: var(--primary);
        display: inline-flex;
        height: 42px;
        justify-content: center;
        width: 42px;
    }

    .auth-header{
        align-items: flex-start;
        flex-direction: column;
    }

    .auth-header > .d-flex{
        align-items: flex-start !important;
    }

    .auth-header .status-cluster{
        align-items: flex-start;
        min-width: auto;
        width: 100%;
    }

    .auth-header .ops-title{
        font-size: 1.28rem;
    }

    .module-label{
        color: var(--primary);
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        line-height: 1;
        text-transform: uppercase;
    }

    .ops-title{
        color: var(--primary-dark);
        font-size: 1.35rem;
        font-weight: 800;
        line-height: 1.2;
        margin-top: 0.35rem;
    }

    .ops-subtitle{
        color: var(--muted);
        font-size: 0.86rem;
        margin-top: 0.2rem;
    }

    .status-cluster{
        align-items: flex-end;
        display: flex;
        flex-direction: column;
        gap: 0.45rem;
        min-width: 210px;
    }

    .status-pill{
        align-items: center;
        animation: pulseLive 2.2s infinite;
        background: #ecfdf5;
        border: 1px solid #86efac;
        border-radius: 999px;
        color: #047857;
        display: inline-flex;
        font-size: 0.72rem;
        font-weight: 800;
        gap: 0.45rem;
        letter-spacing: 0.08em;
        padding: 0.34rem 0.62rem;
        text-transform: uppercase;
        white-space: nowrap;
    }

    .status-dot{
        background: #10b981;
        border-radius: 999px;
        height: 8px;
        width: 8px;
    }

    .status-meta{
        color: var(--muted);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .ops-badges{
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.6rem;
    }

    .ops-badge{
        align-items: center;
        background: #f8fafc;
        border: 1px solid var(--border);
        border-radius: 999px;
        color: var(--muted);
        display: inline-flex;
        font-size: 0.68rem;
        font-weight: 800;
        gap: 0.35rem;
        letter-spacing: 0.06em;
        padding: 0.28rem 0.58rem;
        text-transform: uppercase;
    }

    .telemetry-strip{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(15,23,42,0.03);
        display: grid;
        gap: 0;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        margin-bottom: 0.9rem;
        overflow: hidden;
    }

    .telemetry-item{
        border-right: 1px solid var(--border);
        align-items: center;
        display: flex;
        gap: 0.72rem;
        min-width: 0;
        padding: 0.8rem 0.95rem;
        transition: background 0.22s ease, transform 0.22s ease;
    }

    .telemetry-item:hover{
        background: #f8fafc;
        transform: translateY(-1px);
    }

    .telemetry-icon{
        align-items: center;
        background: #ecfeff;
        border: 1px solid #cffafe;
        border-radius: 8px;
        color: var(--primary);
        display: inline-flex;
        flex: 0 0 34px;
        height: 34px;
        justify-content: center;
    }

    .telemetry-icon{
        align-items: center;
        background: #f8fafc;
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--primary);
        display: inline-flex;
        flex: 0 0 34px;
        height: 34px;
        justify-content: center;
    }

    .telemetry-item:last-child{
        border-right: 0;
    }

    .telemetry-label{
        color: var(--muted);
        font-size: 0.66rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .telemetry-value{
        color: #28677a;
        font-size: 0.88rem;
        font-weight: 800;
        margin-top: 0.22rem;
        overflow-wrap: normal;
        white-space: nowrap;
    }

    @keyframes pulse{
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.45; transform: scale(0.86); }
    }

    .section-title{
        color: var(--text);
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        margin: 0 0 0.9rem 0;
        text-transform: uppercase;
    }

    .section-header{
        align-items: center;
        color: var(--primary-dark);
        display: flex;
        font-size: 0.78rem;
        font-weight: 800;
        justify-content: space-between;
        letter-spacing: 0.09em;
        margin: 1rem 0 0.6rem;
        text-transform: uppercase;
    }

    .section-header:after{
        background: var(--border);
        content: "";
        flex: 1;
        height: 1px;
        margin-left: 0.8rem;
    }

    .section-header i{
        color: var(--primary);
        margin-right: 0.45rem;
    }

    .section-card{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        box-shadow: var(--shadow);
        margin-bottom: 0.9rem;
        padding: 1rem;
    }

    [data-testid="stMetric"]{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(15,23,42,0.03);
        min-height: 96px;
        padding: 0.9rem 1rem;
    }

    [data-testid="stMetricLabel"]{
        color: var(--muted) !important;
        font-size: 0.68rem !important;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    [data-testid="stMetricValue"]{
        color: var(--text) !important;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .kpi-card{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(15,23,42,0.03);
        min-height: 112px;
        padding: 0.95rem 1rem;
        position: relative;
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
        overflow: hidden;
    }

    .kpi-card:hover{
        border-color: var(--border-strong);
        box-shadow: 0 18px 34px -22px rgba(15,23,42,0.36);
        transform: translateY(-5px);
    }

    .kpi-card:before{
        background: var(--primary);
        content: "";
        height: 100%;
        left: 0;
        position: absolute;
        top: 0;
        width: 3px;
    }

    .kpi-card.warning:before{
        background: var(--warning);
    }

    .kpi-card.slate:before{
        background: var(--blue);
    }

    .kpi-topline{
        align-items: center;
        display: flex;
        justify-content: space-between;
        gap: 0.75rem;
    }

    .kpi-icon{
        align-items: center;
        background: #f8fafc;
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--primary);
        display: inline-flex;
        height: 30px;
        justify-content: center;
        width: 30px;
    }

    .kpi-card.warning .kpi-icon{
        color: var(--warning);
    }

    .kpi-card.slate .kpi-icon{
        color: var(--blue);
    }

    .kpi-label{
        color: var(--muted);
        font-size: 0.66rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .kpi-value{
        color: var(--primary-dark);
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1;
        margin-top: 0.65rem;
    }

    .kpi-caption{
        color: var(--muted);
        font-size: 0.78rem;
        font-weight: 600;
        margin-top: 0.55rem;
    }

    .kpi-progress{
        background: #e2e8f0;
        border-radius: 999px;
        height: 4px;
        margin-top: 0.82rem;
        overflow: hidden;
    }

    .kpi-progress span{
        background: var(--primary);
        border-radius: inherit;
        display: block;
        height: 100%;
        width: var(--progress);
        transition: width 0.7s ease;
    }

    .kpi-card.warning .kpi-progress span{
        background: var(--warning);
    }

    .kpi-card.slate .kpi-progress span{
        background: var(--blue);
    }

    .kpi-card.warning .kpi-value{
        color: #b45309;
    }

    .kpi-card.slate .kpi-value{
        color: #1d4ed8;
    }

    .kpi-card.slate .kpi-icon{
        background: var(--blue-soft);
        border-color: #bfdbfe;
    }

    .table-toolbar{
        align-items: center;
        display: flex;
        justify-content: space-between;
        gap: 0.75rem;
        margin-bottom: 0.8rem;
    }

    .record-count{
        color: var(--muted);
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .stButton > button,
    .stDownloadButton > button{
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px;
        padding: 0.56rem 0.9rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        box-shadow: none;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover{
        background: var(--primary-dark) !important;
        color: #ffffff !important;
    }

    .stTextInput input,
    .stDateInput input,
    .stMultiSelect div[data-baseweb="select"]{
        background: var(--surface-muted) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 6px !important;
        min-height: 2.35rem !important;
    }

    .stTextInput input:focus,
    .stDateInput input:focus{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(14,116,144,0.12) !important;
    }

    [data-testid="stForm"]{
        animation: fadeInUp 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        box-shadow: var(--shadow);
        padding: 1rem;
    }

    .stDataFrame{
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
    }

    .sk-footer{
        text-align:center;
        color: var(--muted);
        font-size:0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        padding:1.5rem 0;
        text-transform: uppercase;
    }

    @media (max-width: 1100px){
        .telemetry-strip{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .telemetry-item:nth-child(2){
            border-right: 0;
        }
    }

    @media (max-width: 760px){
        .operational-header{
            align-items: flex-start;
            flex-direction: column;
        }

        .status-cluster{
            align-items: flex-start;
            min-width: auto;
        }

        .telemetry-strip{
            grid-template-columns: 1fr;
        }

        .telemetry-item{
            border-right: 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)

inject_global_styles()

# =========================
# VARIABLES ENTORNO
# =========================

load_dotenv()

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://backend:8000"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:secretpassword@db:5432/skyanalytics"
)

# =========================
# REDIS
# =========================

@st.cache_resource
def get_redis_client():
    return redis.Redis(
        host='redis',
        port=6379,
        db=0,
        decode_responses=True
    )

# =========================
# DATABASE
# =========================

@st.cache_resource
def get_db_connection():
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    return engine

# =========================
# AUTH
# =========================

def authenticate_user(email, password):
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            },
            timeout=10
        )

        if response.status_code == 200:
            return response.json()["access_token"]

        return None

    except Exception as e:
        st.error(f"Error: {e}")
        return None

def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "token" not in st.session_state:
        st.session_state.token = None

    return st.session_state.authenticated

def login_page():

    _, center_col, _ = st.columns([1, 2, 1])

    with center_col:

        st.markdown("""
        <div class="operational-header auth-header">
            <div class="d-flex align-items-center gap-3">
                <div class="brand-icon"><i class="fa-solid fa-plane-departure"></i></div>
                <div>
                    <div class="module-label">SkyAnalytics Access</div>
                    <div class="ops-title">Centro de inteligencia aerolinea</div>
                    <div class="ops-subtitle">
                        Autenticacion requerida para consultar mercados, pasajeros y tendencias.
                    </div>
                </div>
            </div>
            <div class="status-cluster">
                <div class="status-pill"><span class="status-dot"></span>Sistema live</div>
                <div class="status-meta">Operacion segura</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):

            email = st.text_input(
                "Email",
                placeholder="admin@skyanalytics.com"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            submitted = st.form_submit_button(
                "Iniciar sesion"
            )

        if submitted:

            token = authenticate_user(email, password)

            if token:
                st.session_state.authenticated = True
                st.session_state.token = token
                st.success("Login exitoso")
                st.rerun()

            else:
                st.error("Credenciales invalidas")

if not check_auth():
    login_page()
    st.stop()

# =========================
# CONSULTAS
# =========================

@st.cache_data(ttl=300)
def obtener_estadisticas_generales():

    engine = get_db_connection()

    query = """
        SELECT
            COUNT(*) as total_pasajeros,
            COUNT(DISTINCT pais) as paises,
            COUNT(DISTINCT ciudad) as ciudades
        FROM pasajeros
    """

    with engine.connect() as conn:
        result = conn.execute(text(query))
        row = result.fetchone()

    return {
        "total": row[0],
        "paises": row[1],
        "ciudades": row[2]
    }

@st.cache_data(ttl=300)
def obtener_distribucion_paises():

    engine = get_db_connection()

    query = """
        SELECT pais, COUNT(*) as cantidad
        FROM pasajeros
        GROUP BY pais
        ORDER BY cantidad DESC
        LIMIT 15
    """

    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def obtener_tendencia():

    engine = get_db_connection()

    query = """
        SELECT
            DATE_TRUNC('month', fecha_registro)::DATE as mes,
            COUNT(*) as cantidad
        FROM pasajeros
        GROUP BY DATE_TRUNC('month', fecha_registro)
        ORDER BY mes
    """

    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def obtener_pasajeros_filtrados(
    paises=None,
    fecha_inicio=None,
    fecha_fin=None
):

    engine = get_db_connection()

    query = """
        SELECT *
        FROM pasajeros
        WHERE 1=1
    """

    params = {}

    if paises:
        query += " AND pais IN :paises"
        params["paises"] = tuple(paises)

    if fecha_inicio:
        query += " AND fecha_registro >= :fecha_inicio"
        params["fecha_inicio"] = fecha_inicio

    if fecha_fin:
        query += " AND fecha_registro <= :fecha_fin"
        params["fecha_fin"] = fecha_fin

    query += " LIMIT 1000"

    sql_query = text(query)

    if paises:
        sql_query = sql_query.bindparams(
            bindparam("paises", expanding=True)
        )

    with engine.connect() as conn:
        result = conn.execute(sql_query, params)

        df = pd.DataFrame(
            result.fetchall(),
            columns=result.keys()
        )

    return df

# =========================
# UI HELPERS
# =========================

def render_kpi_card(label, value, caption, tone="", icon="fa-chart-line", progress=80):
    st.markdown(
        f"""
        <div class="kpi-card {tone}" style="--progress:{progress}%;">
            <div class="kpi-topline">
                <div class="kpi-label">{label}</div>
                <div class="kpi-icon"><i class="fa-solid {icon}"></i></div>
            </div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-caption">{caption}</div>
            <div class="kpi-progress"><span></span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# HEADER
# =========================

updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

st.markdown("""
<div class="operational-header">
    <div class="d-flex align-items-center gap-3">
        <div class="brand-icon"><i class="fa-solid fa-plane-departure"></i></div>
        <div>
            <div class="module-label">Operational Intelligence</div>
            <div class="ops-title">SkyAnalytics Dashboard</div>
            <div class="ops-subtitle">
                Monitoreo ejecutivo de pasajeros, cobertura geografica y comportamiento historico.
            </div>
            <div class="ops-badges">
                <span class="ops-badge"><i class="fa-solid fa-database"></i> Data-first</span>
                <span class="ops-badge"><i class="fa-solid fa-chart-line"></i> Analytics</span>
                <span class="ops-badge"><i class="fa-solid fa-shield-halved"></i> Ops ready</span>
            </div>
        </div>
    </div>
    <div class="status-cluster">
        <div class="status-pill"><span class="status-dot"></span>Sistema live</div>
        <div class="status-meta">PostgreSQL + FastAPI + Streamlit</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="telemetry-strip">
    <div class="telemetry-item">
        <div class="telemetry-icon"><i class="fa-solid fa-database"></i></div>
        <div>
            <div class="telemetry-label">Data source</div>
            <div class="telemetry-value">PostgreSQL / pasajeros</div>
        </div>
    </div>
    <div class="telemetry-item">
        <div class="telemetry-icon"><i class="fa-solid fa-server"></i></div>
        <div>
            <div class="telemetry-label">API layer</div>
            <div class="telemetry-value">FastAPI :8000</div>
        </div>
    </div>
    <div class="telemetry-item">
        <div class="telemetry-icon"><i class="fa-solid fa-rotate"></i></div>
        <div>
            <div class="telemetry-label">Refresh window</div>
            <div class="telemetry-value">Cache 300s</div>
        </div>
    </div>
    <div class="telemetry-item">
        <div class="telemetry-icon"><i class="fa-solid fa-clock"></i></div>
        <div>
            <div class="telemetry-label">Last render</div>
            <div class="telemetry-value">{updated_at}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================

st.sidebar.markdown("## Control panel")

st.sidebar.markdown("""
<div class="sidebar-callout">
    <strong><i class="fa-solid fa-sliders"></i> Filter scope</strong>
    Segmentacion operacional por pais y rango temporal. Las consultas se limitan
    a 1000 registros para mantener respuesta interactiva.
</div>
""", unsafe_allow_html=True)

engine = get_db_connection()

paises_query = pd.read_sql(
    "SELECT DISTINCT pais FROM pasajeros ORDER BY pais",
    engine
)

paises_disponibles = paises_query["pais"].tolist()

paises_seleccionados = st.sidebar.multiselect(
    "Filtrar pais",
    options=paises_disponibles
)

fecha_inicio = st.sidebar.date_input(
    "Desde",
    datetime.now() - timedelta(days=365)
)

fecha_fin = st.sidebar.date_input(
    "Hasta",
    datetime.now()
)

# =========================
# METRICAS
# =========================

st.markdown('<div class="section-header"><span><i class="fa-solid fa-gauge-high"></i>Resumen general</span></div>', unsafe_allow_html=True)

stats = obtener_estadisticas_generales()

col1, col2, col3 = st.columns(3)

with col1:
    render_kpi_card(
        "Pasajeros",
        f"{stats['total']:,}",
        "Volumen total registrado",
        "primary",
        "fa-users",
        92
    )

with col2:
    render_kpi_card(
        "Paises",
        f"{stats['paises']:,}",
        "Cobertura comercial activa",
        "warning",
        "fa-earth-americas",
        68
    )

with col3:
    render_kpi_card(
        "Ciudades",
        f"{stats['ciudades']:,}",
        "Nodos urbanos detectados",
        "slate",
        "fa-city",
        78
    )

# =========================
# GRAFICOS
# =========================

st.markdown('<div class="section-header"><span><i class="fa-solid fa-chart-area"></i>Distribucion y tendencia</span></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:

    df_paises = obtener_distribucion_paises()

    fig = px.bar(
        df_paises,
        x="cantidad",
        y="pais",
        orientation="h",
        color="cantidad",
        color_continuous_scale=["#0e7490", "#0891b2", "#d97706"],
        labels={
            "cantidad": "Pasajeros",
            "pais": "Pais"
        },
        title="TOP PAISES POR PASAJEROS"
    )

    fig.update_layout(
        bargap=0.22,
        height=390,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#315f72', size=12),
        title_font=dict(size=12, color='#0e7490'),
        coloraxis_showscale=False,
        margin=dict(l=8, r=8, t=36, b=8),
        hoverlabel=dict(bgcolor='#0e7490', font_color='#ffffff', bordercolor='#0e7490')
    )
    fig.update_xaxes(gridcolor='#e2e8f0', zeroline=False, title_font=dict(size=11))
    fig.update_yaxes(categoryorder="total ascending", gridcolor='rgba(0,0,0,0)', title_font=dict(size=11))

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

with col2:

    df_tendencia = obtener_tendencia()

    fig2 = px.line(
        df_tendencia,
        x="mes",
        y="cantidad",
        markers=True,
        labels={
            "mes": "Mes",
            "cantidad": "Registros"
        },
        title="REGISTROS MENSUALES"
    )

    fig2.update_traces(
        line=dict(color="#0e7490", width=3),
        marker=dict(size=7, color="#d97706")
    )
    fig2.update_layout(
        height=390,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#315f72', size=12),
        title_font=dict(size=12, color='#0e7490'),
        margin=dict(l=8, r=8, t=36, b=8),
        hoverlabel=dict(bgcolor='#0e7490', font_color='#ffffff', bordercolor='#0e7490')
    )
    fig2.update_xaxes(gridcolor='#e2e8f0', zeroline=False, title_font=dict(size=11))
    fig2.update_yaxes(gridcolor='#e2e8f0', zeroline=False, title_font=dict(size=11))

    st.plotly_chart(
        fig2,
        use_container_width=True,
        config={"displayModeBar": False}
    )

# =========================
# TABLA
# =========================

st.markdown('<div class="section-header"><span><i class="fa-solid fa-table-list"></i>Datos filtrados</span></div>', unsafe_allow_html=True)

df_filtrado = obtener_pasajeros_filtrados(
    paises=paises_seleccionados,
    fecha_inicio=fecha_inicio,
    fecha_fin=fecha_fin
)

csv = df_filtrado.to_csv(index=False)

st.markdown(f"""
<div class="table-toolbar">
    <div class="record-count">{len(df_filtrado):,} registros visibles</div>
</div>
""", unsafe_allow_html=True)

st.download_button(
    "Descargar CSV",
    csv,
    "pasajeros.csv",
    "text/csv"
)

st.dataframe(
    df_filtrado,
    use_container_width=True,
    height=500
)

# =========================
# FOOTER
# =========================

st.markdown("""
<div class="sk-footer">
SkyAnalytics Dashboard - Operational Edition
</div>
""", unsafe_allow_html=True)
