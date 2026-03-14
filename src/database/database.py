"""
Database management module for PiBot.

This module handles all SQLite database operations including:
- User and profile management
- Item catalog and inventory management
- Balance and points operations
- Text normalization and cleaning utilities
"""

import re
import sqlite3 as sql
import unicodedata
from typing import Optional, Dict, List, Any

from src.config import DATABASE_FILE


def create_database() -> None:
    """Initialize the SQLite database file."""
    conn = sql.connect(DATABASE_FILE)
    conn.commit()
    conn.close()


def create_tables() -> None:
    """
    Create all necessary database tables with proper schema and constraints.
    
    Tables created:
    - usuarios_tb: User accounts and balance
    - items_tb: Item catalog
    - items_usuarios_tb: User inventory (many-to-many relationship)
    - perfiles_tb: User profile information
    """
    conn = sql.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Users table: Stores balance information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_tb (
            id_user INTEGER PRIMARY KEY,
            saldo INTEGER DEFAULT 0
        );
    """)
    
    # Items catalog table: Available items in the shop
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items_tb (
            id_item INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            precio INTEGER NOT NULL,
            imagen TEXT NOT NULL,
            descripcion TEXT,
            mensaje TEXT
        );
    """)
    
    # User inventory table: Many-to-many relationship between users and items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items_usuarios_tb (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user INTEGER NOT NULL,
            id_item INTEGER NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (id_user) REFERENCES usuarios_tb(id_user) ON DELETE CASCADE,
            FOREIGN KEY (id_item) REFERENCES items_tb(id_item) ON DELETE CASCADE,
            UNIQUE(id_user, id_item)
        );
    """)
    
    # Optimize inventory lookups with indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuario ON items_usuarios_tb(id_user);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_item ON items_usuarios_tb(id_item);")
    
    # User profiles table: Additional user information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perfiles_tb (
            id_user INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            nombre TEXT NOT NULL,
            rol TEXT,
            orientacion_sexual TEXT,
            genero TEXT,
            ubicacion TEXT,
            edad INTEGER,
            FOREIGN KEY (id_user) REFERENCES usuarios_tb(id_user) ON DELETE CASCADE
        );
    """)
    
    # Combat/Battle table: Active battles between users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS combates_tb (
            id_combate INTEGER PRIMARY KEY AUTOINCREMENT,
            id_atacante INTEGER NOT NULL,
            id_defensor INTEGER NOT NULL,
            username_atacante TEXT NOT NULL,
            username_defensor TEXT NOT NULL,
            apuesta INTEGER NOT NULL DEFAULT 0,
            hp_atacante INTEGER NOT NULL DEFAULT 20,
            hp_defensor INTEGER NOT NULL DEFAULT 20,
            turno INTEGER NOT NULL DEFAULT 1,
            es_turno_atacante INTEGER NOT NULL DEFAULT 1,
            estado TEXT NOT NULL DEFAULT 'activo',
            ganador INTEGER,
            fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_atacante) REFERENCES usuarios_tb(id_user),
            FOREIGN KEY (id_defensor) REFERENCES usuarios_tb(id_user),
            FOREIGN KEY (ganador) REFERENCES usuarios_tb(id_user)
        );
    """)
    
    # Create indexes for faster combat lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_combate_atacante ON combates_tb(id_atacante);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_combate_defensor ON combates_tb(id_defensor);")
    
    conn.commit()
    conn.close()


def _get_connection() -> sql.Connection:
    """
    Get a database connection.
    
    Returns:
        SQLite connection object
    """
    return sql.connect(DATABASE_FILE)


# ==================== USER OPERATIONS ====================

def insert_user(id_user: int, saldo: int = 0, username: Optional[str] = None,
                nombre: Optional[str] = None) -> bool:
    """
    Create a new user account and profile.
    
    Args:
        id_user: Unique Telegram user ID
        saldo: Initial balance (PiPesos)
        username: Telegram username
        nombre: User's display name
    
    Returns:
        True if successful, False otherwise
    """
    if not id_user:
        print("[ERROR DB] Cannot insert user without valid ID")
        return False
    
    if not nombre or nombre.strip() == "":
        print("[ERROR DB] User must have at least a name")
        return False
    
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Insert into users table
        cursor.execute(
            "INSERT INTO usuarios_tb (id_user, saldo) VALUES (?, ?);",
            (id_user, saldo)
        )
        
        # Insert into profiles table
        cursor.execute(
            "INSERT INTO perfiles_tb (id_user, username, nombre) VALUES (?, ?, ?);",
            (id_user, username, nombre)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR DB] Failed to insert user: {e}")
        return False


def get_campo_usuario(id_user: int, columna: str) -> Optional[Any]:
    """
    Retrieve a specific field from a user's profile or balance.
    
    Args:
        id_user: User's Telegram ID
        columna: Column name to retrieve
    
    Returns:
        Field value or None if not found
    """
    columnas_validas = {
        "nombre", "username", "rol", "orientacion_sexual",
        "genero", "ubicacion", "edad", "saldo", "id_user"
    }
    
    if columna not in columnas_validas:
        print(f"[ERROR DB] Invalid column: {columna}")
        return None
    
    tabla = "perfiles_tb" if columna != "saldo" else "usuarios_tb"
    
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {columna} FROM {tabla} WHERE id_user = ?", (id_user,))
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado[0] if resultado else None
    except Exception as e:
        print(f"[ERROR DB] Error retrieving user field: {e}")
        return None


def update_perfil(id_user: int, **datos) -> bool:
    """
    Update user profile fields.
    
    Args:
        id_user: User's Telegram ID
        **datos: Column-value pairs to update
    
    Returns:
        True if successful, False otherwise
    """
    columnas_validas = {
        "nombre", "username", "rol", "orientacion_sexual",
        "genero", "ubicacion", "edad"
    }
    
    if not datos:
        print("[ERROR DB] No data provided for update")
        return False
    
    # Validate all columns
    for col in datos.keys():
        if col not in columnas_validas:
            print(f"[ERROR DB] Invalid column: {col}")
            return False
    
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        columnas = ", ".join([f"{col} = ?" for col in datos.keys()])
        valores = list(datos.values()) + [id_user]
        
        cursor.execute(f"UPDATE perfiles_tb SET {columnas} WHERE id_user = ?", valores)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR DB] Error updating profile: {e}")
        return False


# ==================== BALANCE OPERATIONS ====================

def update_saldo(id_user: int, saldo: int) -> bool:
    """
    Set user's balance to a specific value.
    
    Args:
        id_user: User's Telegram ID
        saldo: New balance value
    
    Returns:
        True if successful, False otherwise
    """
    if saldo < 0:
        print("[ERROR DB] Balance cannot be negative")
        return False
    
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        cursor.execute(
            "UPDATE usuarios_tb SET saldo = ? WHERE id_user = ?",
            (saldo, id_user)
        )
        
        if cursor.rowcount == 0:
            print("[ERROR DB] User not found")
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR DB] Error updating balance: {e}")
        return False


def dar_puntos(id_user: int, cantidad: int) -> bool:
    """
    Add points to a user's balance.
    
    Args:
        id_user: User's Telegram ID
        cantidad: Amount to add
    
    Returns:
        True if successful, False otherwise
    """
    saldo_actual = get_campo_usuario(id_user, "saldo") or 0
    return update_saldo(id_user, saldo_actual + cantidad)


def quitar_puntos(id_user: int, cantidad: int) -> bool:
    """
    Remove points from a user's balance.
    
    Args:
        id_user: User's Telegram ID
        cantidad: Amount to remove
    
    Returns:
        True if successful, False otherwise
    """
    saldo_actual = get_campo_usuario(id_user, "saldo") or 0
    nuevo_saldo = max(0, saldo_actual - cantidad)
    return update_saldo(id_user, nuevo_saldo)


# ==================== ITEM OPERATIONS ====================

def insert_item(nombre: str, precio: int, ruta_imagen: str,
                descripcion: Optional[str] = None, mensaje: Optional[str] = None) -> bool:
    """
    Add a new item to the catalog.
    
    Args:
        nombre: Item name
        precio: Item price in PiPesos
        ruta_imagen: Path to item image
        descripcion: Optional item description
        mensaje: Optional message sent when using item
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO items_tb (nombre, precio, imagen, descripcion, mensaje) VALUES (?, ?, ?, ?, ?)",
            (nombre, precio, ruta_imagen, descripcion, mensaje)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR DB] Failed to insert item: {e}")
        return False


def get_campo_item(id_item: int, columna: str) -> Optional[Any]:
    """
    Retrieve a specific field from an item.
    
    Args:
        id_item: Item ID
        columna: Column name to retrieve
    
    Returns:
        Field value or None if not found
    """
    columnas_validas = {"id_item", "nombre", "precio", "imagen", "descripcion", "mensaje"}
    
    if columna not in columnas_validas:
        print(f"[ERROR DB] Invalid column: {columna}")
        return None
    
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {columna} FROM items_tb WHERE id_item = ?", (id_item,))
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado[0] if resultado else None
    except Exception as e:
        print(f"[ERROR DB] Error retrieving item: {e}")
        return None


def update_item(id_item: int, **datos) -> bool:
    """
    Update item fields.
    
    Args:
        id_item: Item ID
        **datos: Column-value pairs to update
    
    Returns:
        True if successful, False otherwise
    """
    columnas_validas = {"nombre", "precio", "imagen", "descripcion", "mensaje"}
    
    if not datos:
        print("[ERROR DB] No data provided for update")
        return False
    
    for col in datos.keys():
        if col not in columnas_validas:
            print(f"[ERROR DB] Invalid column: {col}")
            return False
    
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        columnas = ", ".join([f"{col} = ?" for col in datos.keys()])
        valores = list(datos.values()) + [id_item]
        
        cursor.execute(f"UPDATE items_tb SET {columnas} WHERE id_item = ?", valores)
        
        if cursor.rowcount == 0:
            print("[ERROR DB] Item not found")
            return False
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR DB] Error updating item: {e}")
        return False


def get_id_item(nombre: str) -> Optional[int]:
    """
    Get an item ID by its normalized name.
    
    Args:
        nombre: Item name to search for
    
    Returns:
        Item ID or None if not found
    """
    nome_normalizado = normalizar_nombre(nome).capitalize()
    
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_item FROM items_tb WHERE nome = ?", (nome_normalizado,))
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado[0] if resultado else None
    except Exception as e:
        print(f"[ERROR DB] Error getting item ID: {e}")
        return None


# ==================== INVENTORY OPERATIONS ====================

def insert_user_item(id_user: int, id_item: int, cantidad: int = 1) -> bool:
    """
    Add an item to user's inventory or increase quantity.
    
    Args:
        id_user: User's Telegram ID
        id_item: Item ID
        cantidad: Quantity to add
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        # Check if item already in inventory
        cursor.execute(
            "SELECT cantidad FROM items_usuarios_tb WHERE id_user = ? AND id_item = ?",
            (id_user, id_item)
        )
        resultado = cursor.fetchone()
        
        if resultado:
            # Update quantity
            nova_cantidad = resultado[0] + cantidad
            cursor.execute(
                "UPDATE items_usuarios_tb SET cantidad = ? WHERE id_user = ? AND id_item = ?",
                (nova_cantidad, id_user, id_item)
            )
        else:
            # Insert new item
            cursor.execute(
                "INSERT INTO items_usuarios_tb (id_user, id_item, quantidade) VALUES (?, ?, ?)",
                (id_user, id_item, cantidad)
            )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR DB] Error adding item to inventory: {e}")
        return False


def get_items(id_user: int) -> List[Dict[str, Any]]:
    """
    Get all items in a user's inventory.
    
    Args:
        id_user: User's Telegram ID
    
    Returns:
        List of dictionaries with item information
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        
        cursor.execute("""
            SELECT
                items_tb.id_item,
                items_tb.nome,
                items_tb.precio,
                items_tb.imagen,
                items_usuarios_tb.cantidad
            FROM items_usuarios_tb
            INNER JOIN items_tb ON items_tb.id_item = items_usuarios_tb.id_item
            WHERE items_usuarios_tb.id_user = ?
            ORDER BY items_tb.nome
        """, (id_user,))
        
        filas = cursor.fetchall()
        conn.close()
        
        items = [
            {
                "id_item": fila[0],
                "nome": fila[1],
                "precio": fila[2],
                "imagen": fila[3],
                "cantidad": fila[4]
            }
            for fila in filas
        ]
        
        return items
    except Exception as e:
        print(f"[ERROR DB] Error retrieving items: {e}")
        return []


def get_cantidad_item_inventario(id_user: int, id_item: int) -> int:
    """
    Get the quantity of a specific item in user's inventory.
    
    Args:
        id_user: User's Telegram ID
        id_item: Item ID
    
    Returns:
        Quantity (0 if item not in inventory)
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        cursor.execute(
            "SELECT cantidad FROM items_usuarios_tb WHERE id_item = ? AND id_user = ?",
            (id_item, id_user)
        )
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado[0] if resultado else 0
    except Exception as e:
        print(f"[ERROR DB] Error getting item quantity: {e}")
        return 0


def update_cantidad(user_id: int, item_id: int, cantidad: int) -> bool:
    """
    Update the quantity of an item in user's inventory.
    
    Args:
        user_id: User's Telegram ID
        item_id: Item ID
        cantidad: New quantity
    
    Returns:
        True if successful, False otherwise
    """
    if cantidad < 0:
        print("[ERROR DB] Quantity cannot be negative")
        return False
    
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        cursor.execute(
            "UPDATE items_usuarios_tb SET cantidad = ? WHERE id_user = ? AND id_item = ?",
            (cantidad, user_id, item_id)
        )
        
        if cursor.rowcount == 0:
            print("[ERROR DB] Item not found in user inventory")
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR DB] Error updating quantity: {e}")
        return False


def delete_item_user(id_user: int, id_item: int) -> bool:
    """
    Remove an item from user's inventory.
    
    Args:
        id_user: User's Telegram ID
        id_item: Item ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        cursor.execute(
            "DELETE FROM items_usuarios_tb WHERE id_user = ? AND id_item = ?",
            (id_user, id_item)
        )
        
        if cursor.rowcount == 0:
            print("[ERROR DB] Item not found in user inventory")
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR DB] Error deleting item: {e}")
        return False


# ==================== DELETE OPERATIONS ====================

def delete_user(id_user: int) -> bool:
    """
    Delete a user and all associated data (cascading delete).
    
    Args:
        id_user: User's Telegram ID
    
    Returns:
        True if user was deleted, False otherwise
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        cursor.execute("DELETE FROM usuarios_tb WHERE id_user = ?", (id_user,))
        sucesso = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return sucesso
    except Exception as e:
        print(f"[ERROR DB] Error deleting user: {e}")
        return False


def delete_item(id_item: int) -> bool:
    """
    Delete an item from catalog (cascading delete).
    
    Args:
        id_item: Item ID
    
    Returns:
        True if item was deleted, False otherwise
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        cursor.execute("DELETE FROM items_tb WHERE id_item = ?", (id_item,))
        sucesso = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return sucesso
    except Exception as e:
        print(f"[ERROR DB] Error deleting item: {e}")
        return False


# ==================== UTILITY FUNCTIONS ====================

def get_id_user(username: str) -> Optional[int]:
    """
    Get user ID by username.
    
    Args:
        username: Telegram username (without @)
    
    Returns:
        User ID or None if not found
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_user FROM perfiles_tb WHERE username = ?",
            (username,)
        )
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado[0] if resultado else None
    except Exception as e:
        print(f"[ERROR DB] Error getting user ID: {e}")
        return None


def normalizar_nombre(first_name: str, last_name: str = "") -> str:
    """
    Normalize and clean user names.
    
    Removes accents, special characters, and normalizes spaces.
    
    Args:
        first_name: User's first name
        last_name: User's last name
    
    Returns:
        Normalized name string
    """
    nombre_completo = f"{to_plain_text(first_name) or ''} {to_plain_text(last_name) or ''}".strip()
    nombre_completo = re.sub(r'[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñÜü ]+', '', nombre_completo)
    nombre_completo = unicodedata.normalize("NFKD", nombre_completo)
    nombre_completo = ''.join(
        c for c in nombre_completo
        if not unicodedata.combining(c)
    )
    nombre_completo = re.sub(r'\s+', ' ', nombre_completo).strip().lower()
    return nombre_completo


def to_plain_text(s: str, keep_space: bool = False) -> str:
    """
    Convert text to plain ASCII, removing accents and special characters.
    
    Args:
        s: Input string
        keep_space: If True, preserve spaces; if False, remove all spaces
    
    Returns:
        Cleaned ASCII string
    """
    if not isinstance(s, str):
        return ""
    
    out_chars = []
    
    try:
        for ch in s:
            # Normalize combined characters (NFKD separates diacritics)
            ch_nfd = unicodedata.normalize("NFKD", ch)
            
            for ch2 in ch_nfd:
                cat = unicodedata.category(ch2)
                
                # Ignore combining marks (diacritics)
                if cat.startswith("M"):
                    continue
                
                # Ignore control and format characters
                if cat in ("Cc", "Cf"):
                    continue
                
                # Accept ASCII alphanumeric as-is
                if ('0' <= ch2 <= '9' or 'A' <= ch2 <= 'Z' or 'a' <= ch2 <= 'z'):
                    out_chars.append(ch2)
                    continue
                
                # Try to extract base letter from Unicode name
                try:
                    name = unicodedata.name(ch2)
                except ValueError:
                    name = ""
                
                if "LATIN" in name and "LETTER" in name:
                    match = re.search(r"LETTER\s+([A-Z]+[A-Z0-9]*)$", name)
                    if match:
                        token = match.group(1)
                        for c in token:
                            if 'A' <= c <= 'Z':
                                out_chars.append(c.lower())
                        continue
                
                # Treat separator characters as spaces
                if cat.startswith("Z"):
                    out_chars.append(" ")
                    continue
        
        # Join and normalize spaces
        text = "".join(out_chars)
        
        if keep_space:
            text = re.sub(r"\s+", " ", text).strip()
            text = re.sub(r"[^0-9A-Za-z ]+", "", text)
        else:
            text = re.sub(r"[^0-9A-Za-z]+", "", text)
        
        return text.lower()
    except TypeError:
        return ""


def reemplazar_acentos(cadena: str) -> str:
    """
    Replace accented characters with their non-accented equivalents.
    
    Args:
        cadena: Input string
    
    Returns:
        String with accents replaced
    """
    reemplazos = (
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
        ("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U")
    )
    
    for acentuada, normalizada in reemplazos:
        cadena = cadena.replace(acentuada, normalizada)
    
    return cadena


# ==================== COMBAT OPERATIONS ====================

def restart_all_combats() -> None:
    """
    Reset all active combats to 'cancelado' status.
    Called on bot startup to clean up any incomplete combats.
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        cursor.execute(
            "UPDATE combates_tb SET estado = 'cancelado' WHERE estado = 'activo'"
        )
        
        affected_rows = cursor.rowcount
        if affected_rows > 0:
            print(f"[INIT] Cancelled {affected_rows} active combats on startup")
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERROR DB] Error restarting combats: {e}")
