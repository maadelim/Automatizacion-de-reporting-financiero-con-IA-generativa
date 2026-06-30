# 📊 Automatización de Reporting Financiero con IA

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Status](https://img.shields.io/badge/Status-Active-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

Sistema automatizado de análisis y reporting financiero del **IBEX 35** usando Python e Inteligencia Artificial. Descarga datos reales del mercado español, aplica análisis técnico avanzado y genera reportes profesionales en PDF y Excel.

## 🖥️ Vista previa

![Dashboard](dashboard_preview.png)

## 🚀 Características

- 📥 **Descarga automática** de datos reales desde Yahoo Finance (Bolsa de Madrid)
- 📈 **Análisis técnico** con medias móviles (SMA/EMA), RSI y Bandas de Bollinger
- 🤖 **Detección automática** de tendencias y alertas de mercado
- 📄 **Reportes PDF profesionales** con gráficos y tablas
- 📊 **Reportes Excel** con múltiples hojas de análisis
- 🖥️ **Dashboard web interactivo** con Streamlit
- ✅ **Tests unitarios** con pytest
- 🔄 **CI/CD** con GitHub Actions

## 🛠️ Tecnologías

| Tecnología | Uso |
|---|---|
| `yfinance` | Datos reales de mercado |
| `pandas` | Análisis y manipulación de datos |
| `matplotlib` / `seaborn` | Visualizaciones |
| `streamlit` | Dashboard web interactivo |
| `reportlab` | Generación de PDFs |
| `openpyxl` | Reportes Excel |
| `pytest` | Tests unitarios |

## 📦 Instalación

```bash
git clone https://github.com/maadelim/Automatizacion-de-reporting-financiero-con-IA-generativa.git
cd Automatizacion-de-reporting-financiero-con-IA-generativa
pip install -r requirements.txt
```

## ▶️ Uso

### Generar reporte completo:
```bash
python main.py
```

### Lanzar dashboard web:
```bash
streamlit run src/dashboard.py
```

### Ejecutar tests:
```bash
pytest tests/
```

## 📁 Estructura del Proyecto