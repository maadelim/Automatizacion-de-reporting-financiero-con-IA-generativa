# src/data_loader.py
import logging
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional
from src.logger import configurar_logger
from src.config_loader import cargar_config

logger = configurar_logger("data_loader")

def _normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Aplana MultiIndex de columnas si existe y normaliza nombres."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            '_'.join(str(c) for c in col).strip() if col[1] else col[0]
            for col in df.columns
        ]
    # Quedarse solo con el primer segmento (Close_SAN -> Close)
    df.columns = [col.split('_')[0] for col in df.columns]
    return df

def descargar_datos(
    empresas: Optional[dict[str, str]] = None,
    periodo: str = "1y"
) -> dict[str, pd.DataFrame]:
    """
    Descarga datos históricos de Yahoo Finance para las empresas indicadas.

    Args:
        empresas: Diccionario {nombre: ticker}. Si es None, usa config.yaml.
        periodo: Periodo de tiempo (ej: '1y', '6mo', '3mo').

    Returns:
        Diccionario {nombre: DataFrame con OHLCV}.
    """
    if empresas is None:
        config = cargar_config()
        empresas = config["ibex35"]["empresas"]
        periodo = config["ibex35"].get("periodo", periodo)

    datos: dict[str, pd.DataFrame] = {}
    errores: list[str] = []

    for nombre, ticker in empresas.items():
        try:
            logger.info(f"Descargando datos de {nombre} ({ticker})...")
            df = yf.download(ticker, period=periodo, auto_adjust=True, progress=False)

            if df.empty:
                logger.warning(f"Sin datos para {nombre} ({ticker}). Omitiendo.")
                continue

            df = _normalizar_columnas(df)
            df = df.dropna(subset=["Close"])

            logger.info(f"{nombre}: {len(df)} registros descargados.")
            datos[nombre] = df

        except Exception as exc:
            logger.error(f"Error al descargar {nombre} ({ticker}): {exc}")
            errores.append(nombre)

    if errores:
        logger.warning(f"No se pudieron descargar: {', '.join(errores)}")

    return datos

def obtener_resumen(datos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Calcula métricas básicas de resumen para cada empresa.

    Args:
        datos: Resultado de descargar_datos().

    Returns:
        DataFrame con columnas: Empresa, Precio Actual, Precio Inicio,
        Variación (%), Máximo, Mínimo, Volumen Promedio.
    """
    resumen: list[dict] = []

    for nombre, df in datos.items():
        if df.empty or "Close" not in df.columns:
            logger.warning(f"DataFrame vacío o sin columna 'Close' para {nombre}.")
            continue
        try:
            close = df["Close"].dropna()
            if len(close) < 2:
                logger.warning(f"Datos insuficientes para {nombre}.")
                continue

            precio_actual = round(float(close.iloc[-1]), 2)
            precio_inicio = round(float(close.iloc[0]), 2)
            variacion = round((precio_actual - precio_inicio) / precio_inicio * 100, 2)

            resumen.append({
                "Empresa": nombre,
                "Precio Actual": precio_actual,
                "Precio Inicio": precio_inicio,
                "Variación (%)": variacion,
                "Máximo": round(float(df["High"].max()), 2) if "High" in df.columns else None,
                "Mínimo": round(float(df["Low"].min()), 2) if "Low" in df.columns else None,
                "Volumen Promedio": int(df["Volume"].mean()) if "Volume" in df.columns else None,
            })
        except Exception as exc:
            logger.error(f"Error procesando resumen de {nombre}: {exc}")

    return pd.DataFrame(resumen)

EMPRESAS = cargar_config()["ibex35"]["empresas"]