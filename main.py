# main.py
from src.data_loader import descargar_datos, obtener_resumen
from src.analyzer import generar_graficos, analizar_resumen, calcular_indicadores, detectar_tendencia
from src.alerts import detectar_alertas
from src.report_generator import generar_pdf
from src.ai_analyst import generar_analisis_ia
from src.logger import configurar_logger

logger = configurar_logger("main")

def main():
    logger.info("🚀 Iniciando generación de reporte financiero IBEX 35...")

    # 1. Descargar datos
    logger.info("📥 Descargando datos del mercado español...")
    datos = descargar_datos()

    # 2. Resumen básico
    logger.info("📊 Calculando resumen financiero...")
    df_resumen = obtener_resumen(datos)

    # 3. Detectar tendencias por empresa
    logger.info("📈 Detectando tendencias con indicadores técnicos...")
    tendencias = {}
    for nombre, df in datos.items():
        df_ind = calcular_indicadores(df)
        tendencias[nombre] = detectar_tendencia(df_ind)
        logger.info(f"  {nombre}: {tendencias[nombre]}")

    # 4. Detectar alertas
    logger.info("⚠️  Verificando alertas de mercado...")
    df_alertas = detectar_alertas(datos)

    # 5. Generar gráficos técnicos
    logger.info("📉 Generando gráficos con indicadores técnicos...")
    graficos = generar_graficos(datos)

    # 6. Análisis con IA
    logger.info("🤖 Generando análisis con IA (Gemini)...")
    analisis = generar_analisis_ia(df_resumen, df_alertas, tendencias)
    print("\n" + analisis)

    # 7. Generar PDF
    logger.info("📄 Generando reporte PDF...")
    generar_pdf(df_resumen, analisis, graficos)

    logger.info("✅ ¡Proceso completado! Revisa la carpeta 'reports'")

if __name__ == "__main__":
    main()