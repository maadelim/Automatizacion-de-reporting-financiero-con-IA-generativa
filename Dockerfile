# Dockerfile
FROM python:3.11-slim

# Metadatos
LABEL maintainer="maadelim"
LABEL description="Automatización de Reporting Financiero IBEX 35 con IA"

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Instalar dependencias del sistema necesarias para reportlab y matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios de salida
RUN mkdir -p reports logs

# Puerto para Streamlit
EXPOSE 8501

# Comando por defecto: lanzar el dashboard
CMD ["streamlit", "run", "src/dashboard.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
     