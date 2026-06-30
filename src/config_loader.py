# src/config_loader.py
import yaml
import logging
from pathlib import Path

def cargar_config(ruta: str = "config.yaml") -> dict:
    """Carga la configuración desde un archivo YAML."""
    ruta_path = Path(ruta)
    if not ruta_path.exists():
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {ruta}")
    with open(ruta_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)