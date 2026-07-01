# tests/test_analyzer.py
import pandas as pd
import numpy as np
from src.analyzer import calcular_indicadores, detectar_tendencia, analizar_resumen


def crear_df_ohlcv(n: int = 100) -> pd.DataFrame:
    """Crea un DataFrame OHLCV sintético con tendencia alcista."""
    fechas = pd.date_range("2024-01-01", periods=n, freq="B")
    precios = np.linspace(10, 15, n) + np.random.normal(0, 0.05, n)
    return pd.DataFrame({
        "Open": precios * 0.99,
        "High": precios * 1.02,
        "Low": precios * 0.98,
        "Close": precios,
        "Volume": np.random.randint(100_000, 1_000_000, n),
    }, index=fechas)


class TestCalcularIndicadores:

    def test_sma20_calculada(self):
        df = calcular_indicadores(crear_df_ohlcv(100))
        assert "SMA_20" in df.columns
        assert df["SMA_20"].notna().any()

    def test_sma50_calculada(self):
        df = calcular_indicadores(crear_df_ohlcv(100))
        assert "SMA_50" in df.columns
        assert df["SMA_50"].notna().any()

    def test_ema20_calculada(self):
        df = calcular_indicadores(crear_df_ohlcv(100))
        assert "EMA_20" in df.columns
        assert df["EMA_20"].notna().any()

    def test_rsi14_en_rango(self):
        df = calcular_indicadores(crear_df_ohlcv(100))
        rsi = df["RSI_14"].dropna()
        assert (rsi >= 0).all() and (rsi <= 100).all()

    def test_bollinger_superior_mayor_que_inferior(self):
        df = calcular_indicadores(crear_df_ohlcv(100))
        validos = df.dropna(subset=["BB_upper", "BB_lower"])
        assert (validos["BB_upper"] >= validos["BB_lower"]).all()

    def test_atr_positivo(self):
        df = calcular_indicadores(crear_df_ohlcv(100))
        assert "ATR_14" in df.columns
        assert (df["ATR_14"].dropna() >= 0).all()

    def test_no_modifica_df_original(self):
        df_original = crear_df_ohlcv(100)
        cols_antes = set(df_original.columns)
        calcular_indicadores(df_original)
        assert set(df_original.columns) == cols_antes

    def test_columnas_nuevas_aniadidas(self):
        df = calcular_indicadores(crear_df_ohlcv(100))
        for col in ["SMA_20", "SMA_50", "EMA_20", "RSI_14"]:
            assert col in df.columns

    def test_df_pequeño_no_falla(self):
        df = calcular_indicadores(crear_df_ohlcv(10))
        assert isinstance(df, pd.DataFrame)

    def test_sma20_nan_en_primeras_filas(self):
        df = calcular_indicadores(crear_df_ohlcv(100))
        assert df["SMA_20"].iloc[:19].isna().any()

    def test_sma50_nan_en_primeras_filas(self):
        df = calcular_indicadores(crear_df_ohlcv(100))
        assert df["SMA_50"].iloc[:49].isna().any()

    def test_retorna_dataframe(self):
        resultado = calcular_indicadores(crear_df_ohlcv(100))
        assert isinstance(resultado, pd.DataFrame)


class TestDetectarTendencia:

    def test_tendencia_alcista(self):
        df = calcular_indicadores(crear_df_ohlcv(100))
        tendencia = detectar_tendencia(df)
        assert tendencia in ["ALCISTA", "BAJISTA", "LATERAL", "INDETERMINADA"]

    def test_sin_indicadores_devuelve_indeterminada(self):
        df = crear_df_ohlcv(50)
        assert detectar_tendencia(df) == "INDETERMINADA"


class TestAnalizarResumen:

    def crear_resumen(self) -> pd.DataFrame:
        return pd.DataFrame([
            {"Empresa": "Santander", "Variación (%)": 12.5, "Precio Actual": 4.5},
            {"Empresa": "BBVA", "Variación (%)": -8.0, "Precio Actual": 9.2},
            {"Empresa": "Inditex", "Variación (%)": 5.0, "Precio Actual": 45.0},
        ])

    def test_devuelve_string(self):
        assert isinstance(analizar_resumen(self.crear_resumen()), str)

    def test_contiene_mejor_empresa(self):
        resultado = analizar_resumen(self.crear_resumen())
        assert "Santander" in resultado

    def test_contiene_peor_empresa(self):
        resultado = analizar_resumen(self.crear_resumen())
        assert "BBVA" in resultado

    def test_df_vacio_no_falla(self):
        resultado = analizar_resumen(pd.DataFrame())
        assert isinstance(resultado, str)
        assert len(resultado) > 0