# tests/test_data_loader.py
"""Tests del módulo data_loader con mocking de yfinance."""
from __future__ import annotations

import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch
from src.data_loader import descargar_datos, obtener_resumen

N = 60
FECHAS = pd.date_range("2024-01-01", periods=N, freq="B")
PRECIOS = np.linspace(10, 12, N)

DF_MOCK = pd.DataFrame({
    "Open": PRECIOS * 0.99,
    "High": PRECIOS * 1.02,
    "Low": PRECIOS * 0.98,
    "Close": PRECIOS,
    "Volume": [500_000] * N,
}, index=FECHAS)

CONFIG_MOCK = {
    "ibex35": {"empresas": {"TestEmpresa": "TEST.MC"}, "periodo": "1y"},
    "alertas": {"umbral_caida": 3.0, "umbral_subida": 3.0},
    "reportes": {"carpeta_salida": "reports", "dpi_graficos": 100},
}


class TestDescargarDatos:

    @patch("src.data_loader.cargar_config", return_value=CONFIG_MOCK)
    @patch("src.data_loader.yf.download", return_value=DF_MOCK)
    def test_retorna_dict(self, mock_yf, mock_cfg):
        resultado = descargar_datos()
        assert isinstance(resultado, dict)

    @patch("src.data_loader.cargar_config", return_value=CONFIG_MOCK)
    @patch("src.data_loader.yf.download", return_value=DF_MOCK)
    def test_contiene_empresa(self, mock_yf, mock_cfg):
        resultado = descargar_datos()
        assert "TestEmpresa" in resultado

    @patch("src.data_loader.cargar_config", return_value=CONFIG_MOCK)
    @patch("src.data_loader.yf.download", return_value=DF_MOCK)
    def test_df_tiene_columna_close(self, mock_yf, mock_cfg):
        resultado = descargar_datos()
        assert "Close" in resultado["TestEmpresa"].columns

    @patch("src.data_loader.cargar_config", return_value=CONFIG_MOCK)
    @patch("src.data_loader.yf.download", return_value=pd.DataFrame())
    def test_empresa_sin_datos_no_incluida(self, mock_yf, mock_cfg):
        resultado = descargar_datos()
        assert "TestEmpresa" not in resultado

    @patch("src.data_loader.cargar_config", return_value=CONFIG_MOCK)
    @patch("src.data_loader.yf.download", side_effect=Exception("API error"))
    def test_error_de_api_no_rompe_ejecucion(self, mock_yf, mock_cfg):
        resultado = descargar_datos()
        assert isinstance(resultado, dict)


class TestObtenerResumen:

    def test_retorna_dataframe(self):
        datos = {"TestEmpresa": DF_MOCK}
        resultado = obtener_resumen(datos)
        assert isinstance(resultado, pd.DataFrame)

    def test_contiene_columnas_esperadas(self):
        datos = {"TestEmpresa": DF_MOCK}
        resultado = obtener_resumen(datos)
        for col in ["Empresa", "Precio Actual", "Variación (%)"]:
            assert col in resultado.columns

    def test_variacion_calculada_correctamente(self):
        datos = {"TestEmpresa": DF_MOCK}
        resultado = obtener_resumen(datos)
        variacion = resultado.loc[
            resultado["Empresa"] == "TestEmpresa", "Variación (%)"
        ].values[0]
        assert isinstance(variacion, float)

    def test_dict_vacio_retorna_df_vacio(self):
        resultado = obtener_resumen({})
        assert resultado.empty

    def test_df_sin_close_ignorado(self):
        df_sin_close = DF_MOCK.drop(columns=["Close"])
        resultado = obtener_resumen({"SinClose": df_sin_close})
        assert resultado.empty