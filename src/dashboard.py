import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loader import descargar_datos, obtener_resumen, EMPRESAS
from src.analyzer import analizar_resumen
from src.alerts import detectar_alertas

# --- Configuración de página ---
st.set_page_config(
    page_title="IBEX 35 | Financial Analytics",
    page_icon="",
    layout="wide"
)

# --- CSS Profesional estilo Bloomberg ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main { background-color: #0f1117; }
    
    .header-title {
        font-size: 22px;
        font-weight: 600;
        color: #ffffff;
        letter-spacing: 0.5px;
        border-bottom: 1px solid #2d3139;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .subheader {
        font-size: 11px;
        color: #8b9196;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 500;
        margin-bottom: 16px;
    }
    .metric-card {
        background-color: #1a1d23;
        border: 1px solid #2d3139;
        border-radius: 4px;
        padding: 14px 18px;
        margin-bottom: 8px;
    }
    .metric-company {
        font-size: 11px;
        color: #8b9196;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    .metric-price {
        font-size: 24px;
        font-weight: 600;
        color: #ffffff;
        margin: 4px 0;
    }
    .metric-up { color: #00c896; font-size: 13px; font-weight: 500; }
    .metric-down { color: #ff4757; font-size: 13px; font-weight: 500; }
    .divider { border-top: 1px solid #2d3139; margin: 24px 0; }
    
    [data-testid="stSidebar"] {
        background-color: #1a1d23;
        border-right: 1px solid #2d3139;
    }
    [data-testid="stSidebar"] * { color: #c8cdd2 !important; }
    
    div[data-testid="metric-container"] {
        background-color: #1a1d23;
        border: 1px solid #2d3139;
        border-radius: 4px;
        padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="header-title">IBEX 35 — Market Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Real-time equity data · Bolsa de Madrid · Data source: Yahoo Finance</div>', unsafe_allow_html=True)

# --- Sidebar limpio ---
with st.sidebar:
    st.markdown("**PARAMETERS**")
    st.markdown("---")
    periodo = st.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y"],
                          index=3, format_func=lambda x: {
                              "1mo": "1 Month", "3mo": "3 Months",
                              "6mo": "6 Months", "1y": "1 Year", "2y": "2 Years"
                          }[x])
    empresas_sel = st.multiselect("Securities", list(EMPRESAS.keys()),
                                  default=list(EMPRESAS.keys()))
    st.markdown("---")
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
    st.markdown("---")
    st.markdown('<span style="font-size:10px;color:#555;">Data delayed ~15 min. Not financial advice.</span>', unsafe_allow_html=True)

# --- Carga de datos ---
@st.cache_data(ttl=900)
def cargar_datos(periodo):
    return descargar_datos(periodo)

with st.spinner("Fetching market data..."):
    datos = cargar_datos(periodo)
    datos_filtrados = {k: v for k, v in datos.items() if k in empresas_sel}
    df_resumen = obtener_resumen(datos_filtrados)

# --- KPIs ---
st.markdown('<div class="subheader">Market Summary</div>', unsafe_allow_html=True)

if not df_resumen.empty:
    cols = st.columns(len(df_resumen))
    for i, (_, row) in enumerate(df_resumen.iterrows()):
        variacion = row["Variación (%)"]
        color_class = "metric-up" if variacion >= 0 else "metric-down"
        arrow = "+" if variacion >= 0 else ""
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-company">{row['Empresa']}</div>
                <div class="metric-price">€{row['Precio Actual']}</div>
                <div class="{color_class}">{arrow}{variacion}%</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- Gráficos estilo profesional ---
st.markdown('<div class="subheader">Price History</div>', unsafe_allow_html=True)

empresas_lista = list(datos_filtrados.keys())
col1, col2 = st.columns(2)

for i, nombre in enumerate(empresas_lista):
    df = datos_filtrados[nombre]
    if df.empty:
        continue

    fig, ax = plt.subplots(figsize=(8, 3))
    fig.patch.set_facecolor('#1a1d23')
    ax.set_facecolor('#1a1d23')

    close_col = [c for c in df.columns if 'Close' in str(c)]
    if not close_col:
        continue
    close = df[close_col[0]].dropna()

    variacion_color = '#00c896' if float(close.iloc[-1]) >= float(close.iloc[0]) else '#ff4757'
    ax.plot(close.index, close.values, color=variacion_color, linewidth=1.2)
    ax.fill_between(close.index, close.values, alpha=0.08, color=variacion_color)

    ax.set_title(nombre, color='#ffffff', fontsize=11, fontweight='500', pad=10)
    ax.tick_params(colors='#555e6b', labelsize=8)
    ax.spines[:].set_color('#2d3139')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.label.set_color('#8b9196')
    ax.set_ylabel('EUR', color='#8b9196', fontsize=8)
    ax.grid(True, color='#2d3139', linewidth=0.5, alpha=0.7)
    plt.tight_layout()

    if i % 2 == 0:
        col1.pyplot(fig)
    else:
        col2.pyplot(fig)
    plt.close()

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- Tabla de datos ---
st.markdown('<div class="subheader">Data Table</div>', unsafe_allow_html=True)
if not df_resumen.empty:
    def color_variacion(val):
        if isinstance(val, float) and val > 0:
            return 'color: #00c896'
        elif isinstance(val, float) and val < 0:
            return 'color: #ff4757'
        return ''

    st.dataframe(
        df_resumen.style
            .format({"Precio Actual": "€{:.2f}", "Precio Inicio": "€{:.2f}",
                     "Variación (%)": "{:+.2f}%", "Máximo": "€{:.2f}",
                     "Mínimo": "€{:.2f}", "Volumen Promedio": "{:,.0f}"})
            .map(color_variacion, subset=["Variación (%)"]),
        use_container_width=True,
        hide_index=True
    )

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- Alertas ---
st.markdown('<div class="subheader">Market Alerts</div>', unsafe_allow_html=True)
df_alertas = detectar_alertas(datos_filtrados)
if df_alertas.empty:
    st.success("No significant price movements detected.")
else:
    st.dataframe(df_alertas, use_container_width=True, hide_index=True)

st.markdown('<div style="font-size:10px;color:#555;text-align:right;margin-top:20px;">Market data provided by Yahoo Finance. Delayed approximately 15 minutes.</div>', unsafe_allow_html=True)