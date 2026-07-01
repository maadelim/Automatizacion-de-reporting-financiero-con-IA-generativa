# src/report_generator.py
"""
Módulo de generación de informes PDF profesionales.

Genera un informe PDF estructurado con portada, resumen financiero,
análisis de IA y gráficos técnicos de cada empresa del IBEX 35.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.logger import configurar_logger

logger = configurar_logger("report_generator")


def generar_pdf(
    df_resumen: pd.DataFrame,
    analisis: str,
    graficos: dict[str, str],
    carpeta: str = "reports",
) -> Optional[str]:
    """
    Genera un informe PDF profesional con resumen financiero y gráficos.

    Args:
        df_resumen: DataFrame con columnas Empresa, Precio Actual,
                    Precio Inicio, Variación (%), Máximo, Mínimo.
        analisis:   Texto de análisis generado por IA o análisis básico.
        graficos:   Diccionario {nombre_empresa: ruta_imagen}.
        carpeta:    Directorio donde se guarda el PDF. Se crea si no existe.

    Returns:
        Ruta absoluta al PDF generado, o None si ocurrió un error.

    Raises:
        ValueError: Si df_resumen está vacío.
    """
    if df_resumen.empty:
        raise ValueError("df_resumen está vacío: no se puede generar el PDF.")

    try:
        os.makedirs(carpeta, exist_ok=True)
        fecha = datetime.now().strftime("%Y%m%d_%H%M")
        ruta_pdf = os.path.join(carpeta, f"reporte_financiero_{fecha}.pdf")

        doc = SimpleDocTemplate(
            ruta_pdf,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        styles = getSampleStyleSheet()
        contenido = []

        # --- Portada ---
        contenido.append(Paragraph("📊 Reporte Financiero — IBEX 35", styles["Title"]))
        contenido.append(Spacer(1, 0.3 * cm))
        fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        contenido.append(Paragraph(f"Generado: {fecha_str}", styles["Normal"]))
        contenido.append(Spacer(1, 0.8 * cm))

        # --- Tabla de resumen ---
        contenido.append(Paragraph("Resumen de Mercado", styles["Heading2"]))
        contenido.append(Spacer(1, 0.3 * cm))

        columnas = ["Empresa", "Precio Actual", "Precio Inicio", "Variación (%)", "Máximo", "Mínimo"]
        columnas_presentes = [c for c in columnas if c in df_resumen.columns]
        datos_tabla = [columnas_presentes]
        for _, fila in df_resumen.iterrows():
            datos_tabla.append([str(fila.get(c, "N/A")) for c in columnas_presentes])

        tabla = Table(datos_tabla, repeatRows=1)
        tabla.setStyle(
            TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#003366")),
                ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
                ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, 0),  9),
                ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ("GRID",          (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE",      (0, 1), (-1, -1), 8),
            ])
        )
        contenido.append(tabla)
        contenido.append(Spacer(1, 0.8 * cm))

        # --- Análisis de IA ---
        contenido.append(Paragraph("Análisis de Mercado (IA)", styles["Heading2"]))
        contenido.append(Spacer(1, 0.3 * cm))
        for linea in analisis.split("\n"):
            if linea.strip():
                contenido.append(Paragraph(linea.strip(), styles["Normal"]))
                contenido.append(Spacer(1, 0.1 * cm))
        contenido.append(Spacer(1, 0.5 * cm))

        # --- Gráficos técnicos ---
        if graficos:
            contenido.append(Paragraph("Gráficos Técnicos", styles["Heading2"]))
            contenido.append(Spacer(1, 0.3 * cm))
            for nombre, ruta_img in graficos.items():
                if ruta_img and os.path.exists(ruta_img):
                    try:
                        contenido.append(Paragraph(nombre, styles["Heading3"]))
                        contenido.append(Image(ruta_img, width=16 * cm, height=8 * cm))
                        contenido.append(Spacer(1, 0.5 * cm))
                    except Exception as img_exc:
                        logger.warning(f"No se pudo añadir imagen de {nombre}: {img_exc}")

        doc.build(contenido)
        logger.info(f"✅ PDF generado correctamente: {ruta_pdf}")
        return ruta_pdf

    except Exception as exc:
        logger.error(f"❌ Error generando PDF: {exc}", exc_info=True)
        return None