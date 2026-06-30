# tests/test_alerts.py
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from src.alerts import detectar_alertas


CONFIG_MOCK = {
    "alertas": {"umbral_caida": 3.0, "umbral_subida": 3.0},
    "ibex35":  {"empresas": {}, "periodo": "1y"},
    "reportes": {"carpeta_salida": "reports", "dpi_graficos": 100},
    "ia": {"proveedor": "openai", "modelo": "gpt-4o-mini"}
}


def crear_datos_prueba(variacion: float = 0.0, n: int = 60) -> dict:
    """
    Crea datos sintéticos con un movimiento de precio controlado.
    El último día sube o baja según el parámetro 'variacion'.
    """
    fechas  = pd.date_range("2024-01-01", periods=n, freq="B")
    precios = np.ones(n) * 10.0
    precios[-1] = 10.0 * (1 + variacion / 100)
    df = pd.DataFrame({
        "Close":  precios,
        "High":   precios * 1.01,
        "Low":    precios * 0.99,
        "Volume": [1_000_000] * n,
    }, index=fechas)
    return {"EmpresaTest": df}


class TestDetectarAlertas:

    @patch("src.alerts.cargar_config", return_value=CONFIG_MOCK)
    def test_caida_detectada(self, _):
        datos   = crear_datos_prueba(variacion=-5.0)
        alertas = detectar_alertas(datos)
        assert not alertas.empty
        assert "CAÍDA" in alertas.iloc[0]["Tipo"]

    @patch("src.alerts.cargar_config", return_value=CONFIG_MOCK)
    def test_subida_detectada(self, _):
        datos   = crear_datos_prueba(variacion=5.0)
        alertas = detectar_alertas(datos)
        assert not alertas.empty
        assert "SUBIDA" in alertas.iloc[0]["Tipo"]

    @patch("src.alerts.cargar_config", return_value=CONFIG_MOCK)
    def test_mercado_estable_sin_alertas(self, _):
        datos   = crear_datos_prueba(variacion=0.5)
        alertas = detectar_alertas(datos)
        assert alertas.empty

    @patch("src.alerts.cargar_config", return_value=CONFIG_MOCK)
    def test_df_vacio_no_genera_alertas(self, _):
        datos   = {"Vacía": pd.DataFrame()}
        alertas = detectar_alertas(datos)
        assert alertas.empty

    @patch("src.alerts.cargar_config", return_value=CONFIG_MOCK)
    def test_zscore_incluido_en_resultado(self, _):
        datos   = crear_datos_prueba(variacion=-6.0)
        alertas = detectar_alertas(datos)
        assert "Z-Score" in alertas.columns
        assert alertas.iloc[0]["Z-Score"] >= 0

    @patch("src.alerts.cargar_config", return_value=CONFIG_MOCK)
    def test_severidad_alta_con_zscore_elevado(self, _):
        datos   = crear_datos_prueba(variacion=-15.0)
        alertas = detectar_alertas(datos)
        assert not alertas.empty
        assert alertas.iloc[0]["Severidad"] in ["ALTA", "MEDIA"]