"""
Utility functions for PiBot.

This module contains shared utility functions used across handlers and other modules.
"""

import os
import random
from typing import Optional, Tuple


def obtener_gif_aleatorio(nombre_producto: str) -> Optional[str]:
    """
    Get a random GIF from the items folder.
    
    Args:
        nombre_producto: Product/item name (matches folder name)
    
    Returns:
        Path to random GIF file or None if not found
    """
    nombre_carpeta = nombre_producto.lower().replace(" ", "_")
    
    # Get the path to the gifs_items directory
    ruta_carpeta = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "gifs_items",
        nombre_carpeta
    )
    
    ruta_carpeta = os.path.abspath(ruta_carpeta)
    
    # Verify folder exists
    if not os.path.isdir(ruta_carpeta):
        print(f"[WARNING] GIF folder not found: {ruta_carpeta}")
        return None
    
    # List only GIF files
    archivos = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(".gif")]
    
    if not archivos:
        print(f"[WARNING] No GIFs found in: {ruta_carpeta}")
        return None
    
    # Select random GIF
    gif_seleccionado = random.choice(archivos)
    gif_path = os.path.join(ruta_carpeta, gif_seleccionado)
    
    return gif_path


def get_image_path(relative_path: str) -> str:
    """
    Get absolute path to an image in the project.
    
    Args:
        relative_path: Path relative to project root (e.g., "img_items/catalog.png")
    
    Returns:
        Absolute path to the image
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, relative_path)
