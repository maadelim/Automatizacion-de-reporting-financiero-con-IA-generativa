# src/analyzer.py
import logging
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import ta
from src.logger import configurar_logger
from src.config_loader import cargar_config

logger = configurar_logger("analyzer")


def calcular_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade indicadores técnicos reales al DataFrame.

    Indicadores calculados:
    - SMA 20 y SMA 50 (medias móviles simples)
    - EMA 20 (media móvil exponencial)
    - RSI 14 (Relative Strength Index)
    - Bandas de Bollinger (20 períodos, 2 desviaciones)
    - ATR 14 (Average True Range — volatilidad)
    """
    df = df.copy()

    df["SMA_20"] = ta.trend.sma_indicator(df["Close"], window=20)
    df["SMA_50"] = ta.trend.sma_indicator(df["Close"], window=50)
    df["EMA_20"] = ta.trend.ema_indicator(df["Close"], window=20)
    df["RSI_14"] = ta.momentum.rsi(df["Close"], window=14)

    bb = ta.volatility.BollingerBands(df["Close"], window=20, window_dev=2)
    df["BB_upper"] = bb.bollinger_hband()
    df["BB_mid"]   = bb.bollinger_mavg()
    df["BB_lower"] = bb.bollinger_lband()

    if all(c in df.columns for c in ["High", "Low", "Close"]):
        df["ATR_14"] = ta.volatility.average_true_range(
            df["High"], df["Low"], df["Close"], window=14
        )

    return df


def detectar_tendencia(df: pd.DataFrame) -> str:
    """
    Determina la tendencia actual basándose en medias móviles y RSI.

    Returns:
        'ALCISTA', 'BAJISTA', 'LATERAL' o 'INDETERMINADA'
    """
    if "SMA_20" not in df.columns or "SMA_50" not in df.columns:
        return "INDETERMINADA"

    sma20  = df["SMA_20"].iloc[-1]
    sma50  = df["SMA_50"].iloc[-1]
    rsi    = df["RSI_14"].iloc[-1] if "RSI_14" in df.columns else 50
    precio = df["Close"].iloc[-1]

    if pd.isna(sma20) or pd.isna(sma50):
        return "INDETERMINADA"

    if precio > sma20 > sma50 and rsi > 50:
        return "ALCISTA"
    elif precio < sma20 < sma50 and rsi < 50:
        return "BAJISTA"
    else:
        return "LATERAL"


def generar_graficos(
    datos: dict[str, pd.DataFrame],
    carpeta: str = "reports"
) -> list[str]:
    """
    Genera gráficos de precio con indicadores técnicos superpuestos.
    Panel superior: precio + SMA 20/50 + Bandas de Bollinger.
    Panel inferior: RSI con zonas de sobrecompra/sobreventa.
    """
    config = cargar_config()
    dpi = config["reportes"].get("dpi_graficos", 150)
    os.makedirs(carpeta, exist_ok=True)
    graficos: list[str] = []

    for nombre, df in datos.items():
        if df.empty or "Close" not in df.columns:
            continue
        try:
            df_ind = calcular_indicadores(df)

            fig, (ax1, ax2) = plt.subplots(
                2, 1, figsize=(12, 7),
                gridspec_kw={"height_ratios": [3, 1]}
            )
            fig.suptitle(f"{nombre} — Análisis Técnico", fontsize=14, fontweight="bold")

            # Panel superior: precio + medias móviles + Bollinger
            ax1.plot(df_ind.index, df_ind["Close"],
                     color="royalblue", linewidth=1.5, label="Cierre")
            ax1.plot(df_ind.index, df_ind["SMA_20"],
                     color="orange", linewidth=1, linestyle="--", label="SMA 20")
            ax1.plot(df_ind.index, df_ind["SMA_50"],
                     color="red", linewidth=1, linestyle="--", label="SMA 50")

            if "BB_upper" in df_ind.columns:
                ax1.fill_between(
                    df_ind.index,
                    df_ind["BB_lower"],
                    df_ind["BB_upper"],
                    alpha=0.1, color="gray", label="Bollinger"
                )

            ax1.set_ylabel("Precio (€)")
            ax1.legend(fontsize=8, loc="upper left")
            ax1.grid(True, alpha=0.3)

            # Panel inferior: RSI
            if "RSI_14" in df_ind.columns:
                ax2.plot(df_ind.index, df_ind["RSI_14"],
                         color="purple", linewidth=1)
                ax2.axhline(70, color="red",   linestyle="--",
                            linewidth=0.8, alpha=0.7, label="Sobrecompra (70)")
                ax2.axhline(30, color="green", linestyle="--",
                            linewidth=0.8, alpha=0.7, label="Sobreventa (30)")
                ax2.fill_between(df_ind.index, df_ind["RSI_14"], 50,
                                 where=df_ind["RSI_14"] >= 50,
                                 alpha=0.1, color="green")
                ax2.fill_between(df_ind.index, df_ind["RSI_14"], 50,
                                 where=df_ind["RSI_14"] < 50,
                                 alpha=0.1, color="red")
                ax2.set_ylim(0, 100)
                ax2.set_ylabel("RSI (14)")
                ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            ruta = os.path.join(carpeta, f"{nombre}_tecnico.png")
            plt.savefig(ruta, dpi=dpi, bbox_inches="tight")
            plt.close()
            graficos.append(ruta)
            logger.info(f"Gráfico técnico guardado: {ruta}")

        except Exception as exc:
            logger.error(f"Error generando gráfico de {nombre}: {exc}")

    return graficos


def analizar_resumen(df_resumen: pd.DataFrame) -> str:
    """
    Genera un análisis textual del resumen financiero.
    """
    if df_resumen.empty:
        return "Sin datos disponibles para el análisis."

    mejor     = df_resumen.loc[df_resumen["Variación (%)"].idxmax()]
    peor      = df_resumen.loc[df_resumen["Variación (%)"].idxmin()]
    promedio  = round(df_resumen["Variación (%)"].mean(), 2)
    positivas = (df_resumen["Variación (%)"] > 0).sum()
    negativas = (df_resumen["Variación (%)"] < 0).sum()

    return f"""
📊 ANÁLISIS FINANCIERO — IBEX 35
{'='*50}
✅ Mejor rendimiento : {mejor['Empresa']} con +{mejor['Variación (%)']}%
❌ Peor  rendimiento : {peor['Empresa']} con {peor['Variación (%)']}%
📈 Variación promedio: {promedio}%
🟢 Empresas en positivo: {positivas}
🔴 Empresas en negativo: {negativas}
"""