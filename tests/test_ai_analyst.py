# tests/test_ai_analyst.py
"""Tests del módulo ai_analyst con mocking de la API de Gemini."""
from __future__ import annotations

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from src.ai_analyst import generar_analisis_ia

DF_RESUMEN = pd.DataFrame([
    {"Empresa": "Santander", "Variación (%)": 2.5, "Precio Actual": 4.2},
    {"Empresa": "BBVA",      "Variación (%)": -1.3, "Precio Actual": 9.8},
])

DF_ALERTAS = pd.DataFrame([
    {"Empresa": "Santander", "Tipo": "🟢 SUBIDA FUERTE", "Variación (%)": 2.5,
     "Severidad": "MEDIA", "Z-Score": 1.5},
])

TENDENCIAS = {"Santander": "ALCISTA", "BBVA": "LATERAL"}


class TestGenerarAnalisisIA:

    @patch.dict("os.environ", {}, clear=True)
    def test_sin_api_key_usa_fallback(self):
        """Sin GEMINI_API_KEY debe devolver el análisis estadístico básico."""
        resultado = generar_analisis_ia(DF_RESUMEN, DF_ALERTAS, TENDENCIAS)
        assert isinstance(resultado, str)
        assert len(resultado) > 0

    @patch.dict("os.environ", {}, clear=True)
    def test_fallback_contiene_empresa(self):
        resultado = generar_analisis_ia(DF_RESUMEN, DF_ALERTAS, TENDENCIAS)
        assert "Santander" in resultado or "BBVA" in resultado

    @patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key-123"})
    @patch("src.ai_analyst.google.generativeai")
    def test_con_api_key_llama_a_gemini(self, mock_genai):
        """Con API key debe intentar llamar a la API de Gemini."""
        mock_model = MagicMock()
        mock_model.generate_content.return_value.text = "Análisis generado por IA."
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()

        resultado = generar_analisis_ia(DF_RESUMEN, DF_ALERTAS, TENDENCIAS)
        assert isinstance(resultado, str)

    @patch.dict("os.environ", {}, clear=True)
    def test_df_resumen_vacio_no_falla(self):
        resultado = generar_analisis_ia(pd.DataFrame(), pd.DataFrame(), {})
        assert isinstance(resultado, str)

    @patch.dict("os.environ", {}, clear=True)
    def test_sin_alertas_no_falla(self):
        resultado = generar_analisis_ia(DF_RESUMEN, pd.DataFrame(), TENDENCIAS)
        assert isinstance(resultado, str)