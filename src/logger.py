# src/logger.py
import logging
import sys
from pathlib import Path

def configurar_logger(nombre: str = "ibex35", nivel: int = logging.INFO) -> logging.Logger:
    """Configura y devuelve un logger con salida a consola y archivo."""
    Path("logs").mkdir(exist_ok=True)
    
    logger = logging.getLogger(nombre)
    logger.setLevel(nivel)
    
    if logger.handlers:  # Evitar duplicados si se llama varias veces
        return logger

    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler de consola
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formato)
    logger.addHandler(ch)

    # Handler de archivo
    fh = logging.FileHandler("logs/ibex35.log", encoding="utf-8")
    fh.setFormatter(formato)
    logger.addHandler(fh)

    return logger