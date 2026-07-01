# src/dashboard.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from src.data_loader import descargar_datos, obtener_resumen
from src.analyzer import calcular_indicadores, detectar_tendencia
from src.alerts import detectar_alertas

# --- Configuración de página ---
st.set_page_config(
    page_title="IBEX 35 | Market Analytics",
    page_icon=None,
    layout="wide"
)

# --- CSS estilo terminal financiera profesional ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d0f14;
    color: #c9d1d9;
}

.main { background-color: #0d0f14; }

section[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #21262d;
}

.dashboard-header {
    font-size: 13px;
    font-weight: 500;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 2px;
    border-bottom: 1px solid #21262d;
    padding-bottom: 12px;
    margin-bottom: 24px;
}

.dashboard-title {
    font-size: 20px;
    font-weight: 600;
    color: #e6edf3;
    letter-spacing: 0.5px;
}

.kpi-card {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 4px;
    padding: 16px 20px;
    margin-bottom: 8px;
}

.kpi-label {
    font-size: 10px;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 500;
    margin-bottom: 6px;
}

.kpi-value {
    font-size: 22px;
    font-weight: 600;
    color: #e6edf3;
    line-height: 1.2;
}

.kpi-sub {
    font-size: 12px;
    color: #8b949e;
    margin-top: 4px;
}

.positive { color: #3fb950; }
.negative { color: #f85149; }
.neutral  { color: #d29922; }

.section-title {
    font-size: 11px;
    font-weight: 600;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid #21262d;
}

.alert-high {
    background-color: #2d1117;
    border-left: 3px solid #f85149;
    padding: 10px 14px;
    border-radius: 2px;
    margin-bottom: 6px;
    font-size: 13px;
}

.alert-medium {
    background-color: #2d2208;
    border-left: 3px solid #d29922;
    padding: 10px 14px;
    border-radius: 2px;
    margin-bottom: 6px;
    font-size: 13px;
}

.footer {
    font-size: 10px;
    color: #484f58;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 32px;
    padding-top: 16px;
    border-top: 1px solid #21262d;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #21262d;
    border-radius: 4px;
}

.stSelectbox label { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
.stButton > button {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    width: 100%;
}
.stButton > button:hover {
    background-color: #30363d;
    border-color: #8b949e;
}
</style>
""", unsafe_allow_html=True)


# --- Carga de datos con caché ---
@st.cache_data(ttl=300)
def cargar_datos(periodo: str):
    datos     = descargar_datos(periodo=periodo)
    df_resumen = obtener_resumen(datos)
    tendencias = {}
    for nombre, df in datos.items():
        df_ind = calcular_indicadores(df)
        tendencias[nombre] = detectar_tendencia(df_ind)
    df_alertas = detectar_alertas(datos)
    return datos, df_resumen, tendencias, df_alertas


# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="kpi-label">Market Parameters</div>', unsafe_allow_html=True)
    st.markdown("---")

    periodo = st.selectbox(
        "Analysis Period",
        options=["1mo", "3mo", "6mo", "1y", "2y"],
        index=3,
        format_func=lambda x: {
            "1mo": "1 Month",
            "3mo": "3 Months",
            "6mo": "6 Months",
            "1y":  "1 Year",
            "2y":  "2 Years"
        }[x]
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown('<div class="kpi-label" style="font-size:9px;">Data refreshes automatically every 5 min</div>',
                unsafe_allow_html=True)


# --- Header principal ---
st.markdown("""
<div class="dashboard-header">
    IBEX 35 &nbsp;&middot;&nbsp; Real-Time Market Analytics &nbsp;&middot;&nbsp;
    Bolsa de Madrid &nbsp;&middot;&nbsp; Source: Yahoo Finance
</div>
""", unsafe_allow_html=True)


# --- Carga ---
with st.spinner("Loading market data..."):
    try:
        datos, df_resumen, tendencias, df_alertas = cargar_datos(periodo)
    except Exception as e:
        st.error(f"Error loading market data: {e}")
        st.stop()

if df_resumen.empty:
    st.warning("No market data available for the selected period.")
    st.stop()


# --- KPIs ---
mejor  = df_resumen.loc[df_resumen["Variación (%)"].idxmax()]
peor   = df_resumen.loc[df_resumen["Variación (%)"].idxmin()]
media  = round(df_resumen["Variación (%)"].mean(), 2)
n_pos  = int((df_resumen["Variación (%)"] > 0).sum())
n_neg  = int((df_resumen["Variación (%)"] < 0).sum())
n_alrt = len(df_alertas)

col1, col2, col3, col4, col5 = st.columns(5)

color_media = "positive" if media >= 0 else "negative"

with col1:
    st.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Avg. Variation</div>
        <div class="kpi-value {color_media}">{media:+.2f}%</div>
        <div class="kpi-sub">Period return average</div>
    </div>''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Top Performer</div>
        <div class="kpi-value">{mejor["Empresa"]}</div>
        <div class="kpi-sub positive">{mejor["Variación (%)"]:+.2f}%</div>
    </div>''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Worst Performer</div>
        <div class="kpi-value">{peor["Empresa"]}</div>
        <div class="kpi-sub negative">{peor["Variación (%)"]:+.2f}%</div>
    </div>''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Advancing / Declining</div>
        <div class="kpi-value"><span class="positive">{n_pos}</span> / <span class="negative">{n_neg}</span></div>
        <div class="kpi-sub">Stocks in period</div>
    </div>''', unsafe_allow_html=True)

with col5:
    alrt_color = "negative" if n_alrt > 0 else "positive"
    st.markdown(f'''<div class="kpi-card">
        <div class="kpi-label">Active Alerts</div>
        <div class="kpi-value {alrt_color}">{n_alrt}</div>
        <div class="kpi-sub">Market alerts triggered</div>
    </div>''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- Tabla de mercado ---
st.markdown('<div class="section-title">Market Summary</div>', unsafe_allow_html=True)

df_display = df_resumen.copy()
df_display["Trend"] = df_display["Empresa"].map(tendencias)

trend_map = {
    "ALCISTA":       "Bullish",
    "BAJISTA":       "Bearish",
    "LATERAL":       "Sideways",
    "INDETERMINADA": "N/A"
}
df_display["Trend"] = df_display["Trend"].map(trend_map)
df_display["Variación (%)"] = df_display["Variación (%)"].apply(lambda x: f"{x:+.2f}%")
df_display["Precio Actual"] = df_display["Precio Actual"].apply(lambda x: f"{x:,.2f} EUR")
df_display["Máximo"]        = df_display["Máximo"].apply(lambda x: f"{x:,.2f} EUR" if x else "N/A")
df_display["Mínimo"]        = df_display["Mínimo"].apply(lambda x: f"{x:,.2f} EUR" if x else "N/A")

df_display = df_display.rename(columns={
    "Empresa":      "Company",
    "Precio Actual":"Last Price",
    "Variación (%)" :"Return (%)",
    "Máximo":       "High",
    "Mínimo":       "Low",
})

st.dataframe(
    df_display[["Company", "Last Price", "Return (%)", "High", "Low", "Trend"]],
    use_container_width=True,
    hide_index=True,
    height=430
)

st.markdown("<br>", unsafe_allow_html=True)


# --- Alertas ---
if not df_alertas.empty:
    st.markdown('<div class="section-title">Market Alerts</div>', unsafe_allow_html=True)
    for _, row in df_alertas.iterrows():
        css_class = "alert-high" if row.get("Severidad") == "ALTA" else "alert-medium"
        st.markdown(f'''<div class="{css_class}">
            <strong>{row["Empresa"]}</strong> &nbsp;|&nbsp;
            {row["Tipo"]} &nbsp;|&nbsp;
            Return: <strong>{row["Variación (%)"]:+.2f}%</strong> &nbsp;|&nbsp;
            Z-Score: {row["Z-Score"]} &nbsp;|&nbsp;
            Severity: <strong>{row["Severidad"]}</strong>
        </div>''', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# --- Gráfico técnico ---
st.markdown('<div class="section-title">Technical Analysis</div>', unsafe_allow_html=True)

empresas_lista = df_resumen["Empresa"].tolist()
empresa_sel    = st.selectbox("Select company", empresas_lista, label_visibility="collapsed")

if empresa_sel and empresa_sel in datos:
    df_emp = datos[empresa_sel]
    df_ind = calcular_indicadores(df_emp)
    tendencia_sel = tendencias.get(empresa_sel, "N/A")

    st.markdown(f'<div style="font-size:11px;color:#8b949e;margin-bottom:12px;">'
                f'{empresa_sel} &nbsp;|&nbsp; Trend: {trend_map.get(tendencia_sel, "N/A")} &nbsp;|&nbsp; '
                f'SMA 20 / SMA 50 / RSI 14 / Bollinger Bands</div>',
                unsafe_allow_html=True)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(14, 6),
        gridspec_kw={"height_ratios": [3, 1]},
        facecolor="#0d0f14"
    )
    ax1.set_facecolor("#161b22")
    ax2.set_facecolor("#161b22")

    ax1.plot(df_ind.index, df_ind["Close"],
             color="#58a6ff", linewidth=1.5, label="Close")
    if "SMA_20" in df_ind.columns:
        ax1.plot(df_ind.index, df_ind["SMA_20"],
                 color="#d29922", linewidth=0.9, linestyle="--", label="SMA 20")
    if "SMA_50" in df_ind.columns:
        ax1.plot(df_ind.index, df_ind["SMA_50"],
                 color="#f85149", linewidth=0.9, linestyle="--", label="SMA 50")
    if "BB_upper" in df_ind.columns:
        ax1.fill_between(df_ind.index, df_ind["BB_lower"], df_ind["BB_upper"],
                         alpha=0.06, color="#58a6ff")
        ax1.plot(df_ind.index, df_ind["BB_upper"],
                 color="#58a6ff", linewidth=0.4, linestyle=":", alpha=0.5)
        ax1.plot(df_ind.index, df_ind["BB_lower"],
                 color="#58a6ff", linewidth=0.4, linestyle=":", alpha=0.5)

    ax1.set_ylabel("Price (EUR)", color="#8b949e", fontsize=10)
    ax1.tick_params(colors="#8b949e", labelsize=9)
    ax1.legend(fontsize=8, loc="upper left",
               facecolor="#161b22", edgecolor="#21262d", labelcolor="#c9d1d9")
    ax1.grid(True, alpha=0.08, color="#30363d")
    for spine in ax1.spines.values():
        spine.set_edgecolor("#21262d")

    if "RSI_14" in df_ind.columns:
        rsi = df_ind["RSI_14"].dropna()
        idx = df_ind.index[-len(rsi):]
        ax2.plot(idx, rsi, color="#8957e5", linewidth=1)
        ax2.axhline(70, color="#f85149", linestyle="--", linewidth=0.7, alpha=0.6)
        ax2.axhline(30, color="#3fb950", linestyle="--", linewidth=0.7, alpha=0.6)
        ax2.fill_between(idx, rsi, 50, where=rsi >= 50, alpha=0.08, color="#3fb950")
        ax2.fill_between(idx, rsi, 50, where=rsi  < 50, alpha=0.08, color="#f85149")
        ax2.set_ylim(0, 100)
        ax2.set_ylabel("RSI (14)", color="#8b949e", fontsize=10)
        ax2.tick_params(colors="#8b949e", labelsize=9)
        ax2.grid(True, alpha=0.08, color="#30363d")
        for spine in ax2.spines.values():
            spine.set_edgecolor("#21262d")

    plt.tight_layout(h_pad=0.5)
    st.pyplot(fig, use_container_width=True)
    plt.close()


# --- Footer ---
st.markdown("""
<div class="footer">
    IBEX 35 Market Analytics &nbsp;&middot;&nbsp;
    Data provided by Yahoo Finance &nbsp;&middot;&nbsp;
    Powered by Python &amp; Gemini AI &nbsp;&middot;&nbsp;
    For informational purposes only. Not financial advice.
</div>
""", unsafe_allow_html=True)