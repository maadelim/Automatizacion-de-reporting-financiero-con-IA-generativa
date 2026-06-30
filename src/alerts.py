# src/alerts.py
import pandas as pd
from src.logger import configurar_logger
from src.config_loader import cargar_config

logger = configurar_logger("alerts")


def detectar_alertas(
    datos: dict[str, pd.DataFrame],
    umbral_caida: float | None = None,
    umbral_subida: float | None = None
) -> pd.DataFrame:
    """
    Detecta movimientos bruscos usando umbral adaptativo basado en la
    volatilidad histórica de cada activo.

    En lugar de un umbral fijo del 5% para todas las empresas,
    calcula cuántas desviaciones estándar (Z-Score) se aleja el
    movimiento del día respecto al comportamiento histórico del activo.

    Args:
        datos: Resultado de descargar_datos().
        umbral_caida: Caída en % para disparar alerta (default: config.yaml).
        umbral_subida: Subida en % para disparar alerta (default: config.yaml).

    Returns:
        DataFrame con las alertas detectadas y su severidad.
    """
    config = cargar_config()
    umbral_caida  = umbral_caida  or config["alertas"]["umbral_caida"]
    umbral_subida = umbral_subida or config["alertas"]["umbral_subida"]

    alertas: list[dict] = []

    for nombre, df in datos.items():
        if df.empty or "Close" not in df.columns or len(df) < 5:
            logger.warning(f"Datos insuficientes para calcular alertas de {nombre}.")
            continue
        try:
            close    = df["Close"].dropna()
            retornos = close.pct_change().dropna() * 100

            ultimo    = float(close.iloc[-1])
            penultimo = float(close.iloc[-2])
            variacion = (ultimo - penultimo) / penultimo * 100

            # Volatilidad histórica: desviación estándar de retornos diarios
            volatilidad = float(retornos.std())

            # Z-Score: cuántas desviaciones estándar es el movimiento de hoy
            z_score = abs(variacion) / volatilidad if volatilidad > 0 else 0

            alerta_tipo = None
            if variacion <= -umbral_caida:
                alerta_tipo = "🔴 CAÍDA BRUSCA"
            elif variacion >= umbral_subida:
                alerta_tipo = "🟢 SUBIDA FUERTE"

            if alerta_tipo:
                severidad = "ALTA" if z_score > 2 else "MEDIA"
                alertas.append({
                    "Empresa":         nombre,
                    "Tipo":            alerta_tipo,
                    "Variación (%)":   round(variacion, 2),
                    "Precio Actual":   round(ultimo, 2),
                    "Volatilidad (σ)": round(volatilidad, 2),
                    "Z-Score":         round(z_score, 2),
                    "Severidad":       severidad,
                })
                logger.warning(
                    f"{alerta_tipo} | {nombre} | {round(variacion, 2)}% | "
                    f"Z-Score: {round(z_score, 2)} | Severidad: {severidad}"
                )

        except Exception as exc:
            logger.error(f"Error procesando alertas de {nombre}: {exc}")

    df_alertas = pd.DataFrame(alertas) if alertas else pd.DataFrame()

    if not df_alertas.empty:
        logger.warning(f"⚠️  Total alertas detectadas: {len(df_alertas)}")
    else:
        logger.info("✅ Sin alertas. Mercado estable.")

    return df_alertas