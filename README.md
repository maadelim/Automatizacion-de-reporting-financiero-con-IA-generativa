# 📊 Automatización de Reporting Financiero con IA — IBEX 35

Sistema profesional de análisis y reporting financiero del IBEX 35 construido con Python e Inteligencia Artificial Generativa. Descarga datos reales del mercado español, aplica análisis técnico avanzado, genera alertas inteligentes y produce informes PDF con análisis redactado por Gemini AI.

![CI](https://github.com/maadelim/Automatizacion-de-reporting-financiero-con-IA-generativa/actions/workflows/ci.yml/badge.svg)

---

## 🚀 Características

- 📥 **Descarga automática** de datos reales desde Yahoo Finance (14 empresas del IBEX 35)
- 📈 **Indicadores técnicos reales**: SMA 20/50, EMA 20, RSI 14, Bandas de Bollinger, ATR 14
- 🔍 **Detección de tendencias** por activo: ALCISTA, BAJISTA o LATERAL
- ⚠️ **Sistema de alertas** con volatilidad adaptativa y Z-Score por empresa
- 🤖 **Análisis con IA Generativa** (Google Gemini) para generar informes en lenguaje natural
- 📄 **Informes PDF profesionales** con gráficos técnicos y tablas de resumen
- 🖥️ **Dashboard web interactivo** estilo Bloomberg con Streamlit
- ✅ **18 tests unitarios** con mocking de APIs externas
- 🔄 **CI/CD automático** con GitHub Actions en cada push
- 📋 **Logging profesional** con timestamps y niveles INFO, WARNING, ERROR
- ⚙️ **Configuración externa** en YAML sin tocar el código

---

## 🛠️ Tecnologías

| Tecnología | Uso |
|---|---|
| yfinance | Datos reales de mercado |
| pandas | Análisis y manipulación de datos |
| ta | Indicadores técnicos SMA, EMA, RSI, Bollinger, ATR |
| matplotlib | Visualizaciones y gráficos técnicos |
| streamlit | Dashboard web interactivo |
| google-generativeai | Análisis en lenguaje natural con Gemini |
| reportlab | Generación de PDFs profesionales |
| pytest | 18 tests unitarios con mocking |
| pyyaml | Configuración externa en YAML |
| python-dotenv | Gestión segura de API Keys |

---

## 📦 Instalación

```bash
git clone https://github.com/maadelim/Automatizacion-de-reporting-financiero-con-IA-generativa.git
cd Automatizacion-de-reporting-financiero-con-IA-generativa
pip install -r requirements.txt
```

Crea un archivo `.env` en la raíz del proyecto con tu API Key de Gemini:

GEMINI_API_KEY=tu_clave_aqui


---

## ▶️ Uso

Generar reporte completo con análisis IA:

```bash
python main.py
```

Lanzar dashboard web interactivo:

```bash
streamlit run src/dashboard.py
```

Ejecutar los 18 tests unitarios:

```bash
pytest tests/ -v
```

## 🐳 Uso con Docker

Construir imagen:
```bash
docker build -t ibex35-reporter .
```

Ejecutar dashboard:
```bash
docker run -p 8501:8501 -e GEMINI_API_KEY=tu_clave ibex35-reporter
```

Generar reporte PDF:
```bash
docker run -e GEMINI_API_KEY=tu_clave -v $(pwd)/reports:/app/reports \
  ibex35-reporter python main.py
```

---

## 📁 Estructura del Proyecto
├── src/
│   ├── data_loader.py       # Descarga y limpieza de datos con yfinance
│   ├── analyzer.py          # Indicadores técnicos: SMA, EMA, RSI, Bollinger, ATR
│   ├── alerts.py            # Alertas con Z-Score y volatilidad adaptativa
│   ├── ai_analyst.py        # Análisis con Google Gemini AI
│   ├── dashboard.py         # Dashboard interactivo con Streamlit
│   ├── report_generator.py  # Generación de PDFs profesionales
│   ├── config_loader.py     # Carga de configuración YAML
│   └── logger.py            # Sistema de logging profesional
├── tests/
│   ├── test_analyzer.py     # 12 tests de indicadores técnicos
│   └── test_alerts.py       # 6 tests de alertas con mocking
├── .github/workflows/
│   └── ci.yml               # CI/CD: tests automáticos en cada push
├── config.yaml              # Configuración externa sin tocar el código
├── logs/                    # Logs de ejecución con timestamps
├── reports/                 # PDFs generados automáticamente
├── .env                     # API Keys (no se sube a GitHub)
├── .gitignore
├── requirements.txt
└── main.py                  # Punto de entrada principal
---

## ⚙️ Configuración

Todo el comportamiento del sistema se controla desde `config.yaml` sin modificar ningún archivo Python. Puedes cambiar el periodo de análisis, añadir o quitar empresas del IBEX 35, ajustar los umbrales de alerta o modificar la calidad de los gráficos simplemente editando el archivo de configuración.

---

## 🔒 Seguridad

Las API Keys se gestionan mediante variables de entorno en `.env`, que está excluido de Git mediante `.gitignore`. Las credenciales nunca se exponen en el código ni en el repositorio público.

---

## 👤 Autor

**maadelim** — Proyecto de automatización financiera con Python e IA Generativa