import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, bindparam
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import redis
import json

# ==================== CONFIGURACIÓN STREAMLIT ====================
st.set_page_config(
    page_title="SkyAnalytics Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar variables de entorno
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

# ==================== AUTENTICACIÓN ====================
def authenticate_user(email, password):
    """Autenticar contra la API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def check_auth():
    """Verificar si el usuario está autenticado"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "token" not in st.session_state:
        st.session_state.token = None
    return st.session_state.authenticated

def login_page():
    """Página de login"""
    st.markdown('<div class="main-header">🔐 SkyAnalytics - Login</div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="admin@skyanalytics.com")
        password = st.text_input("Password", type="password", placeholder="admin123")
        submitted = st.form_submit_button("Iniciar sesion")
        
        if submitted:
            token = authenticate_user(email, password)
            if token:
                st.session_state.authenticated = True
                st.session_state.token = token
                st.success("Login exitoso!")
                st.rerun()
            else:
                st.error("Credenciales inválidas")

# Verificar autenticación
if not check_auth():
    login_page()
    st.stop()

# Usuario autenticado, continuar con el dashboard

# ==================== CONEXIÓN A REDIS ====================
@st.cache_resource
def get_redis_client():
    """Obtener cliente Redis (cached)"""
    return redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# ==================== CONEXIÓN A BASE DE DATOS ====================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:secretpassword@db:5432/skyanalytics"
)

@st.cache_resource
def get_db_connection():
    """
    Crear conexión a la base de datos (cached para reutilizar)
    """
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    return engine

# ==================== FUNCIONES DE DATOS CON CACHÉ ====================
@st.cache_data(ttl=300)  # Cachear por 5 minutos
def obtener_estadisticas_generales():
    """Obtener estadísticas generales de pasajeros"""
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_pasajeros,
                    COUNT(DISTINCT pais) as paises_origen,
                    COUNT(DISTINCT ciudad) as ciudades,
                    MAX(fecha_registro) as fecha_ultimo_registro
                FROM pasajeros
            """))
            row = result.fetchone()
            if row:
                return {
                    'total_pasajeros': row[0],
                    'paises_origen': row[1],
                    'ciudades': row[2],
                    'fecha_ultimo_registro': row[3]
                }
            else:
                return None
    except Exception as e:
        st.error(f"Error al obtener estadísticas: {e}")
        return None

@st.cache_data(ttl=300)
def obtener_distribucion_paises():
    """Obtener distribución de pasajeros por país (con caché Redis)"""
    cache_key = "distribucion_paises"

    redis_client = None
    try:
        redis_client = get_redis_client()
        # Intentar obtener de caché
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return pd.read_json(cached_data)
    except Exception:
        # Si Redis no esta disponible, continuamos con consulta directa a BD.
        redis_client = None

    try:
        engine = get_db_connection()
        query = """
            SELECT pais, COUNT(*) as cantidad
            FROM pasajeros
            GROUP BY pais
            ORDER BY cantidad DESC
            LIMIT 50
        """
        df = pd.read_sql(query, engine)
        
        # Guardar en caché por 5 minutos si Redis esta disponible
        if redis_client is not None:
            redis_client.setex(cache_key, 300, df.to_json())
        
        return df
    except Exception as e:
        st.error(f"Error al obtener distribución por país: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def obtener_segmentacion_tarjetas():
    """Obtener segmentación de pasajeros por tipo de tarjeta"""
    try:
        engine = get_db_connection()
        query = """
            SELECT 
                CASE 
                    WHEN substr(tarjeta_credito, 1, 1) = '4' THEN 'Visa'
                    WHEN substr(tarjeta_credito, 1, 1) = '5' THEN 'Mastercard'
                    WHEN substr(tarjeta_credito, 1, 1) = '3' THEN 'American Express'
                    ELSE 'Otras'
                END as tipo_tarjeta,
                COUNT(*) as cantidad
            FROM pasajeros
            GROUP BY tipo_tarjeta
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error al obtener segmentación de tarjetas: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def obtener_pasajeros_filtrados(paises=None, fecha_inicio=None, fecha_fin=None):
    """Obtener pasajeros con filtros opcionales"""
    try:
        engine = get_db_connection()

        query = """
            SELECT *
            FROM pasajeros
            WHERE 1=1
        """
        params = {}
        has_paises = bool(paises)

        if has_paises:
            query += " AND pais IN :paises"
            params["paises"] = tuple(paises)

        if fecha_inicio:
            query += " AND fecha_registro >= :fecha_inicio"
            params["fecha_inicio"] = fecha_inicio

        if fecha_fin:
            query += " AND fecha_registro <= :fecha_fin"
            params["fecha_fin"] = fecha_fin

        query += " ORDER BY id DESC LIMIT 1000"

        sql_query = text(query)
        if has_paises:
            sql_query = sql_query.bindparams(bindparam("paises", expanding=True))

        with engine.connect() as conn:
            result = conn.execute(sql_query, params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df
    except Exception as e:
        st.error(f"Error al obtener pasajeros filtrados: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def obtener_tendencia_registro():
    """Obtener tendencia de registros por mes"""
    try:
        engine = get_db_connection()
        query = """
            SELECT 
                DATE_TRUNC('month', fecha_registro)::DATE as mes,
                COUNT(*) as cantidad
            FROM pasajeros
            GROUP BY DATE_TRUNC('month', fecha_registro)
            ORDER BY mes ASC
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error al obtener tendencia: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=1800)
def obtener_paises_disponibles():
    """Obtener paises para filtros (cache largo para acelerar carga inicial)."""
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            paises_query = conn.execute(text("SELECT DISTINCT pais FROM pasajeros ORDER BY pais"))
            return [row[0] for row in paises_query.fetchall()]
    except Exception as e:
        st.error(f"Error al obtener paises: {e}")
        return []

# ==================== FUNCIÓN PARA BUSCAR PASAJERO EN API ====================
def buscar_pasajero_por_email(email):
    """Buscar un pasajero específico usando la API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/pasajeros/buscar/por-correo",
            params={"correo": email},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"Pasajero no encontrado: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error al conectar con la API: {e}")
        return None

# ==================== INTERFAZ PRINCIPAL ====================
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(180deg, #f8fbff 0%, #eef5ff 100%);
            font-family: Arial, sans-serif;
        }
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #0d6efd;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            color: #6c757d;
            margin-bottom: 1.2rem;
        }
        .section-card {
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 14px;
            padding: 1rem 1.2rem;
            box-shadow: 0 8px 20px rgba(13, 110, 253, 0.08);
            margin-bottom: 1rem;
        }
        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #0d6efd;
            margin-bottom: 0.75rem;
        }
        [data-testid="stMetric"] {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(39, 89, 152, 0.08);
        }
        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #dee2e6;
        }
        .stButton > button {
            background: linear-gradient(90deg, #0d6efd, #0b5ed7);
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.45rem 0.9rem;
        }
        .stButton > button:hover {
            filter: brightness(0.95);
        }
        .stDownloadButton > button {
            border-radius: 10px;
            border: 1px solid #0d6efd;
            color: #0d6efd;
            background: white;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">✈️ SkyAnalytics - Cerebro Analítico</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Dashboard estratégico para gestión y análisis de datos de pasajeros</div>', unsafe_allow_html=True)

# ==================== BARRA LATERAL - FILTROS ====================
st.sidebar.markdown("### 🎯 Filtros y Controles")
modo_rapido = st.sidebar.toggle("⚡ Carga rapida", value=True, help="Evita consultas pesadas al abrir.")

# Obtener países únicos para el selector (cacheado) bajo demanda en modo rapido.
if "paises_disponibles" not in st.session_state:
    st.session_state.paises_disponibles = []

if modo_rapido:
    if st.sidebar.button("🌍 Cargar lista de paises", key="load_countries"):
        st.session_state.paises_disponibles = obtener_paises_disponibles()
else:
    st.session_state.paises_disponibles = obtener_paises_disponibles()

paises_disponibles = st.session_state.paises_disponibles

# Filtro de países
paises_seleccionados = st.sidebar.multiselect(
    "🌍 Seleccionar Países",
    options=paises_disponibles if paises_disponibles else [],
    default=[]
)

# Filtro de fechas
st.sidebar.write("📅 Rango de Fechas")
col_fecha1, col_fecha2 = st.sidebar.columns(2)
with col_fecha1:
    fecha_inicio = st.date_input(
        "Desde",
        value=datetime.now() - timedelta(days=365),
        key="fecha_inicio"
    )
with col_fecha2:
    fecha_fin = st.date_input(
        "Hasta",
        value=datetime.now(),
        key="fecha_fin"
    )

# Buscador de pasajero
st.sidebar.markdown("---")
st.sidebar.write("🔍 Buscar Pasajero Específico")
email_busqueda = st.sidebar.text_input(
    "Ingresa el email del pasajero",
    placeholder="ejemplo@email.com"
)

# ==================== SECCIÓN 1: ESTADÍSTICAS GENERALES ====================
st.markdown("---")
st.markdown("### 📊 Estadísticas Generales")
st.markdown('<div class="section-card">', unsafe_allow_html=True)

stats = obtener_estadisticas_generales()
mostrar_stats = True
if modo_rapido:
    if "mostrar_stats" not in st.session_state:
        st.session_state.mostrar_stats = False
    if st.button("📈 Cargar estadisticas", key="btn_stats"):
        st.session_state.mostrar_stats = True
    mostrar_stats = st.session_state.mostrar_stats

if mostrar_stats and stats:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👥 Total Pasajeros",
            f"{stats['total_pasajeros']:,}",
            delta="sistema activo"
        )
    
    with col2:
        st.metric(
            "🌍 Países",
            f"{stats['paises_origen']:,}",
            delta="cobertura global"
        )
    
    with col3:
        st.metric(
            "🏙️ Ciudades",
            f"{stats['ciudades']:,}",
            delta="mercados locales"
        )
    
    with col4:
        if stats['fecha_ultimo_registro']:
            dias_atras = (datetime.now().date() - stats['fecha_ultimo_registro']).days
            st.metric(
                "📅 Último Registro",
                f"Hace {dias_atras} días",
                delta=str(stats['fecha_ultimo_registro'])
            )
elif not mostrar_stats:
    st.info("En modo rapido, las estadisticas se cargan bajo demanda.")
st.markdown('</div>', unsafe_allow_html=True)

# ==================== SECCIÓN 2: VISUALIZACIONES ESTRATÉGICAS ====================
st.markdown("---")
st.markdown("### 🎨 Análisis Estratégico")
st.markdown('<div class="section-card">', unsafe_allow_html=True)
if modo_rapido:
    st.info("Modo rapido activo: los graficos pesados se cargan solo bajo demanda.")
    cargar_analitica = st.button("📊 Cargar Analitica Completa", key="btn_analitica")
else:
    cargar_analitica = True

if cargar_analitica:
    # Row 1: Distribución por país y Segmentación de tarjetas
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Distribución de Pasajeros por País (Top 15)**")
        df_paises = obtener_distribucion_paises()
        if not df_paises.empty:
            fig_mapa = px.bar(
                df_paises.head(15),
                x='cantidad',
                y='pais',
                orientation='h',
                color='cantidad',
                color_continuous_scale='Viridis',
                title="Top 15 Países"
            )
            fig_mapa.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_mapa, use_container_width=True)
        else:
            st.info("No hay datos disponibles")

    with col2:
        st.write("**Segmentación de Mercado por Tarjeta**")
        df_tarjetas = obtener_segmentacion_tarjetas()
        if not df_tarjetas.empty:
            fig_tarjetas = px.pie(
                df_tarjetas,
                values='cantidad',
                names='tipo_tarjeta',
                title="Distribución de Tarjetas",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_tarjetas.update_layout(height=400)
            st.plotly_chart(fig_tarjetas, use_container_width=True)
        else:
            st.info("No hay datos disponibles")

    # Row 2: Tendencia de registros
    st.write("**Tendencia de Registros por Mes**")
    df_tendencia = obtener_tendencia_registro()
    if not df_tendencia.empty:
        fig_tendencia = px.line(
            df_tendencia,
            x='mes',
            y='cantidad',
            markers=True,
            title="Crecimiento de Pasajeros",
            line_shape="spline"
        )
        fig_tendencia.update_layout(height=350, hovermode='x unified')
        fig_tendencia.update_xaxes(title="Fecha")
        fig_tendencia.update_yaxes(title="Cantidad de Registros")
        st.plotly_chart(fig_tendencia, use_container_width=True)
    else:
        st.info("No hay datos disponibles")
st.markdown('</div>', unsafe_allow_html=True)

# ==================== SECCIÓN 3: BÚSQUEDA DE PASAJERO ====================
st.markdown("---")
st.markdown("### 🔍 Búsqueda de Pasajero")
st.markdown('<div class="section-card">', unsafe_allow_html=True)

if email_busqueda:
    with st.spinner("Buscando pasajero..."):
        pasajero = buscar_pasajero_por_email(email_busqueda)
        if pasajero:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Nombre:** {pasajero.get('nombre_completo', 'N/A')}")
                st.write(f"**Email:** {pasajero.get('correo', 'N/A')}")
                st.write(f"**Ciudad:** {pasajero.get('ciudad', 'N/A')}")
                st.write(f"**País:** {pasajero.get('pais', 'N/A')}")
            
            with col2:
                st.write(f"**Dirección:** {pasajero.get('direccion', 'N/A')}")
                st.write(f"**Tarjeta Crédito:** {pasajero.get('tarjeta_credito', 'N/A')[-4:]}")
                st.write(f"**Tarjeta Débito:** {pasajero.get('tarjeta_debito', 'N/A')[-4:]}")
                st.write(f"**Fecha Registro:** {pasajero.get('fecha_registro', 'N/A')}")
else:
    st.info("Ingresa un email en la barra lateral para buscar un pasajero específico")
st.markdown('</div>', unsafe_allow_html=True)

# ==================== SECCIÓN 4: TABLA DE DATOS FILTRADOS ====================
st.markdown("---")
st.markdown("### 📋 Datos Filtrados")
st.markdown('<div class="section-card">', unsafe_allow_html=True)

if st.button("🔄 Actualizar Datos", key="refresh_button"):
    st.cache_data.clear()
    st.rerun()
aplicar_filtros = st.button("✅ Aplicar Filtros", key="apply_filters_button")
if "mostrar_filtrados" not in st.session_state:
    st.session_state.mostrar_filtrados = False
if aplicar_filtros:
    st.session_state.mostrar_filtrados = True

df_filtrado = pd.DataFrame()
if st.session_state.mostrar_filtrados:
    with st.spinner("Consultando datos filtrados..."):
        df_filtrado = obtener_pasajeros_filtrados(
            paises=paises_seleccionados if paises_seleccionados else None,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

if not df_filtrado.empty:
    st.write(f"Mostrando {len(df_filtrado)} pasajeros")
    
    # Permitir descargar como CSV
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="📥 Descargar CSV",
        data=csv,
        file_name="pasajeros_export.csv",
        mime="text/csv"
    )
    
    st.dataframe(df_filtrado, use_container_width=True, height=400)
else:
    if st.session_state.mostrar_filtrados:
        st.info("No hay pasajeros que coincidan con los filtros seleccionados")
    else:
        st.info("Presiona 'Aplicar Filtros' para cargar resultados")
st.markdown('</div>', unsafe_allow_html=True)

# ==================== PIE DE PÁGINA ====================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
    SkyAnalytics Dashboard v1.0 | Datos en tiempo real | Última actualización: Cache TTL 5 min
    </div>
""", unsafe_allow_html=True)
