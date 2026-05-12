"""
Tema visual SaaS (claro / oscuro) con glassmorphism ligero.

Centralizar CSS aquí mantiene `app.py` enfocado en layout y datos.
"""


def build_css(*, dark: bool) -> str:
    if dark:
        bg = "#0b0f14"
        surface = "rgba(22, 28, 36, 0.72)"
        surface_solid = "#121c27"
        border = "rgba(148, 163, 184, 0.12)"
        text = "#e8eef7"
        muted = "#94a3b8"
        primary = "#38bdf8"
        primary_dark = "#0ea5e9"
        shadow = "0 18px 50px rgba(0,0,0,0.45)"
    else:
        bg = "#f4f6fb"
        surface = "rgba(255,255,255,0.78)"
        surface_solid = "#ffffff"
        border = "rgba(15, 23, 42, 0.08)"
        text = "#0f172a"
        muted = "#64748b"
        primary = "#0284c7"
        primary_dark = "#0369a1"
        shadow = "0 12px 40px rgba(15, 23, 42, 0.08)"

    return f"""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" rel="stylesheet">
    <style>
      :root {{
        --bg: {bg};
        --surface: {surface};
        --surface-solid: {surface_solid};
        --border: {border};
        --text: {text};
        --muted: {muted};
        --primary: {primary};
        --primary-dark: {primary_dark};
        --shadow: {shadow};
      }}
      html, body, [data-testid="stAppViewContainer"] {{
        background: radial-gradient(1200px 600px at 10% -10%, rgba(56,189,248,0.12), transparent 55%),
                    radial-gradient(900px 500px at 90% 0%, rgba(99,102,241,0.10), transparent 50%),
                    var(--bg) !important;
        color: var(--text) !important;
        font-family: 'Inter', system-ui, sans-serif;
      }}
      [data-testid="stHeader"] {{
        background: var(--surface) !important;
        backdrop-filter: blur(16px);
        border-bottom: 1px solid var(--border);
      }}
      [data-testid="stSidebar"] {{
        background: var(--surface) !important;
        backdrop-filter: blur(18px);
        border-right: 1px solid var(--border);
      }}
      #MainMenu, footer, [data-testid="stDecoration"], [data-testid="stToolbar"] {{
        display: none !important;
      }}
      .glass {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        box-shadow: var(--shadow);
        backdrop-filter: blur(14px);
      }}
      .topbar {{
        display: flex; align-items: center; justify-content: space-between;
        gap: 1rem; padding: 0.85rem 1rem; margin-bottom: 1rem;
      }}
      .pill {{
        display: inline-flex; align-items: center; gap: 0.45rem;
        padding: 0.35rem 0.65rem; border-radius: 999px; font-size: 0.72rem;
        font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;
        border: 1px solid var(--border); color: var(--muted);
      }}
      .pill-live {{
        border-color: rgba(16,185,129,0.35);
        color: #10b981; background: rgba(16,185,129,0.08);
      }}
      .pill-offline {{
        border-color: rgba(248,113,113,0.35);
        color: #f87171; background: rgba(248,113,113,0.08);
      }}
      .kpi {{
        padding: 1rem 1.1rem; border-radius: 16px; position: relative; overflow: hidden;
        border: 1px solid var(--border); background: var(--surface);
        box-shadow: var(--shadow); min-height: 112px;
      }}
      .kpi::before {{
        content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
        background: linear-gradient(180deg, var(--primary), #6366f1);
      }}
      .kpi-label {{ color: var(--muted); font-size: 0.68rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }}
      .kpi-value {{ font-size: 1.85rem; font-weight: 800; margin-top: 0.5rem; color: var(--text); }}
      .kpi-caption {{ font-size: 0.78rem; color: var(--muted); margin-top: 0.45rem; font-weight: 600; }}
      .section-title {{
        font-size: 0.78rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase;
        color: var(--muted); margin: 1.25rem 0 0.75rem;
      }}
      .auth-card {{
        max-width: 420px; margin: 0 auto; padding: 1.5rem; border-radius: 20px;
        border: 1px solid var(--border); background: var(--surface);
        box-shadow: var(--shadow); backdrop-filter: blur(16px);
      }}
      .auth-brand {{
        font-weight: 800; font-size: 1.35rem; letter-spacing: -0.02em; color: var(--text);
      }}
      .auth-sub {{ color: var(--muted); font-size: 0.9rem; margin-top: 0.35rem; }}
      .stButton > button, .stDownloadButton > button {{
        background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        font-weight: 700 !important; padding: 0.55rem 1rem !important;
      }}
      .stTextInput input {{
        border-radius: 10px !important; border: 1px solid var(--border) !important;
        background: var(--surface-solid) !important; color: var(--text) !important;
      }}
      [data-testid="stMetric"] {{
        background: var(--surface) !important; border: 1px solid var(--border) !important;
        border-radius: 14px !important; box-shadow: var(--shadow) !important;
      }}
      div[data-testid="stExpander"] details {{
        border: 1px solid var(--border); border-radius: 12px; background: var(--surface);
      }}
    </style>
    """
