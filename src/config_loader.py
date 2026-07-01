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
    # src/config_loader.py
"""Carga y valida la configuración externa del proyecto desde config.yaml."""
from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

import yaml


@functools.lru_cache(maxsize=1)
def cargar_config(ruta: str = "config.yaml") -> dict[str, Any]:
    """
    Carga la configuración desde un archivo YAML con caché en memoria.

    El decorador lru_cache garantiza que el archivo solo se lee una vez
    por ejecución, evitando I/O innecesario en llamadas repetidas.

    Args:
        ruta: Ruta al archivo YAML. Por defecto 'config.yaml' en la raíz.

    Returns:
        Diccionario con la configuración completa del proyecto.

    Raises:
        FileNotFoundError: Si el archivo no existe en la ruta indicada.
        ValueError: Si el YAML no contiene las claves mínimas requeridas.
    """
    ruta_path = Path(ruta)
    if not ruta_path.exists():
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {ruta}")

    with open(ruta_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    _validar_config(config)
    return config


def _validar_config(config: dict[str, Any]) -> None:
    """Valida que el config tenga las claves mínimas necesarias."""
    claves_requeridas = ["ibex35", "alertas", "reportes"]
    for clave in claves_requeridas:
        if clave not in config:
            raise ValueError(
                f"La clave '{clave}' es obligatoria en config.yaml pero no fue encontrada."
            )
    if "empresas" not in config["ibex35"]:
        raise ValueError("config.yaml debe contener 'ibex35.empresas'.")