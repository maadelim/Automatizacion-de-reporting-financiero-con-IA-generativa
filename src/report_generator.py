from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import cm
from datetime import datetime
import os

def generar_pdf(df_resumen, analisis, graficos, carpeta="reports"):
    os.makedirs(carpeta, exist_ok=True)
    fecha = datetime.now().strftime("%Y%m%d_%H%M")
    ruta_pdf = os.path.join(carpeta, f"reporte_financiero_{fecha}.pdf")

    doc = SimpleDocTemplate(ruta_pdf, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    contenido = []

    # Título
    titulo = Paragraph("📊 Reporte Financiero Automatizado - IBEX 35", styles["Title"])
    contenido.append(titulo)
    contenido.append(Spacer(1, 0.5*cm))

    # Fecha
    fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    contenido.append(Paragraph(f"Generado el: {fecha_str}", styles["Normal"]))
    contenido.append(Spacer(1, 0.5*cm))

    # Análisis texto
    for linea in analisis.strip().split("\n"):
        contenido.append(Paragraph(linea.strip(), styles["Normal"]))
    contenido.append(Spacer(1, 0.5*cm))

    # Tabla resumen
    datos_tabla = [["Empresa", "Precio Actual", "Variación (%)", "Máximo", "Mínimo"]]
    for _, row in df_resumen.iterrows():
        datos_tabla.append([
            row["Empresa"],
            f"€{row['Precio Actual']}",
            f"{row['Variación (%)']}%",
            f"€{row['Máximo']}",
            f"€{row['Mínimo']}"
        ])

    tabla = Table(datos_tabla, colWidths=[4*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    contenido.append(tabla)
    contenido.append(Spacer(1, 0.5*cm))

    # Gráficos
    for ruta in graficos:
        if os.path.exists(ruta):
            contenido.append(Image(ruta, width=16*cm, height=6*cm))
            contenido.append(Spacer(1, 0.3*cm))

    doc.build(contenido)
    print(f"\n✅ Reporte PDF generado: {ruta_pdf}")
    return ruta_pdf