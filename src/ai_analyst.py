# src/ai_analyst.py
import os
import pandas as pd
from dotenv import load_dotenv
from src.logger import configurar_logger
from src.config_loader import cargar_config

load_dotenv()
logger = configurar_logger("ai_analyst")


def generar_analisis_ia(
    df_resumen: pd.DataFrame,
    df_alertas: pd.DataFrame,
    tendencias: dict[str, str]
) -> str:
    """
    Genera un análisis financiero profesional usando Gemini de Google.
    Si no hay API Key configurada, usa el análisis estadístico básico.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        logger.warning("GEMINI_API_KEY no encontrada en .env. Usando análisis básico.")
        return _analisis_fallback(df_resumen, df_alertas, tendencias)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        modelo = genai.GenerativeModel("gemini-1.5-flash")

        contexto = _construir_contexto(df_resumen, df_alertas, tendencias)
        prompt = f"""Eres un analista financiero experto especializado en la Bolsa española y el IBEX 35.
Analiza los siguientes datos de mercado y genera un informe profesional conciso (máximo 250 palabras)
que incluya: resumen del estado del mercado, empresas destacadas, señales técnicas relevantes,
alertas activas si las hay, y una perspectiva de corto plazo.

DATOS:
{contexto}

Responde en español con tono profesional y claro."""

        respuesta = modelo.generate_content(prompt)
        analisis  = respuesta.text
        logger.info("✅ Análisis generado por Gemini correctamente.")
        return analisis

    except Exception as exc:
        logger.error(f"Error al llamar a Gemini: {exc}. Usando análisis básico.")
        return _analisis_fallback(df_resumen, df_alertas, tendencias)


def _construir_contexto(
    df_resumen: pd.DataFrame,
    df_alertas: pd.DataFrame,
    tendencias: dict[str, str]
) -> str:
    """Construye el texto de contexto para el prompt de Gemini."""
    lineas = ["=== RESUMEN DEL MERCADO ==="]
    for _, fila in df_resumen.iterrows():
        tendencia = tendencias.get(fila["Empresa"], "N/D")
        lineas.append(
            f"- {fila['Empresa']}: Precio={fila['Precio Actual']}€ | "
            f"Variación={fila['Variación (%)']}% | Tendencia={tendencia}"
        )

    if not df_alertas.empty:
        lineas.append("\n=== ALERTAS ACTIVAS ===")
        for _, alerta in df_alertas.iterrows():
            lineas.append(
                f"- {alerta['Empresa']}: {alerta['Tipo']} "
                f"({alerta['Variación (%)']}%) | "
                f"Severidad: {alerta['Severidad']} | Z-Score: {alerta['Z-Score']}"
            )
    else:
        lineas.append("\n=== SIN ALERTAS ACTIVAS — Mercado estable ===")

    return "\n".join(lineas)


def _analisis_fallback(
    df_resumen: pd.DataFrame,
    df_alertas: pd.DataFrame,
    tendencias: dict[str, str]
) -> str:
    """Análisis estadístico cuando no hay API Key disponible."""
    if df_resumen.empty:
        return "Sin datos disponibles."

    mejor  = df_resumen.loc[df_resumen["Variación (%)"].idxmax()]
    peor   = df_resumen.loc[df_resumen["Variación (%)"].idxmin()]
    media  = round(df_resumen["Variación (%)"].mean(), 2)
    n_pos  = (df_resumen["Variación (%)"] > 0).sum()
    n_neg  = (df_resumen["Variación (%)"] < 0).sum()
    alcistas = [e for e, t in tendencias.items() if t == "ALCISTA"]
    bajistas = [e for e, t in tendencias.items() if t == "BAJISTA"]

    return f"""
📊 ANÁLISIS FINANCIERO — IBEX 35
{'='*50}
Mercado {'mayoritariamente positivo' if n_pos > n_neg else 'mayoritariamente negativo'}.
Variación promedio del período: {media}%

✅ Mejor rendimiento : {mejor['Empresa']} (+{mejor['Variación (%)']}%)
❌ Peor  rendimiento : {peor['Empresa']} ({peor['Variación (%)']}%)
🟢 Empresas en positivo : {n_pos} | 🔴 En negativo: {n_neg}
📈 Tendencias alcistas  : {', '.join(alcistas) if alcistas else 'Ninguna'}
📉 Tendencias bajistas  : {', '.join(bajistas) if bajistas else 'Ninguna'}
⚠️  Alertas activas     : {len(df_alertas)}
"""