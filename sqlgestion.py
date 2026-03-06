import re
import sqlite3 as sql
import unicodedata

def createDB():
    conn = sql.connect("usuarios.db")
    conn.commit()
    conn.close()
def createTable():
    conn = sql.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_tb (
            id_user INTEGER PRIMARY KEY,
            saldo INTEGER
        );
        """)   
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items_tb (
            id_item INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio INTEGER NOT NULl,
            imagen TEXT NOT NULL
        );
        """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items_usuarios_tb(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user INTEGER NOT NULL,
            id_item INTEGER NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (id_user) REFERENCES usuarios_tb(id_user) ON DELETE CASCADE,
            FOREIGN KEY (id_item) REFERENCES items_tb(id_item) ON DELETE CASCADE
        )
        """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuario ON items_usuarios_tb(id_user);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_item ON items_usuarios_tb(id_item);")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perfiles_tb (
            id_user INTEGER PRIMARY KEY,   -- misma id que en usuarios
            username TEXT,
            nombre TEXT NOT NULL,
            rol TEXT,
            orientacion_sexual TEXT,
            genero TEXT,
            ubicacion TEXT,
            edad INTEGER,
            FOREIGN KEY (id_user) REFERENCES usuarios_tb(id_user) ON DELETE CASCADE
        );
        """)

    conn.commit()
    conn.close()
def connect():
    return sql.connect("usuarios.db")

def insert_user(id_user=-1,saldo=0,username=None,nombre=None):
    if id_user == -1 or id_user == None:
        print("[ERROR BD] No se puede ingresar un usuario que no tiene una id: ")
        return False
    if nombre == None or nombre == "":
        print("[ERROR BD] Todos los usuarios deben de tener al menos un nombre")
        return False
    
    try:
        conn = connect()
        cursor = conn.cursor()
        instruccion = "INSERT INTO usuarios_tb (id_user, saldo) VALUES (?, ?);"
        cursor.execute(instruccion, (id_user,saldo))
        instruccion = (f"INSERT INTO perfiles_tb (id_user,username,nombre) VALUES (?, ?, ?);")
        cursor.execute(instruccion,(id_user,username,nombre))
    except Exception as e:
        print(f"[ERROR BD] Ha ocurrido un error al realizar la insercion del usuarios: {e}")
        return False
    conn.commit()
    conn.close()
    return True
def insert_item(nombre,precio,ruta_imagen):
    conn = connect()
    cursor = conn.cursor()
    try:
        instruccion = ("INSERT INTO items_tb (nombre,precio,imagen) VALUES (?,?,?)")
        cursor.execute(instruccion,(nombre,precio,ruta_imagen))
    except Exception as e:
        print(f"[ERROR BD] No se ha podido ingresar el item: {e}")
        return False
    conn.commit()
    conn.close()
    return True
def insert_user_item(id_user,id_item,cantidad):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT cantidad
        FROM items_usuarios_tb
        WHERE id_user = ? AND id_item = ?
    """,(id_user,id_item)
    )
    resultado = cursor.fetchone()
    if resultado:
        cantidad_actual = resultado[0]
        nueva_cantidad = cantidad_actual + cantidad

        cursor.execute(
            """
            UPDATE items_usuarios_tb
            SET cantidad = ?
            WHERE id_user = ? AND id_item = ?
            """,(nueva_cantidad,id_user,id_item)
        )
    else:
        cursor.execute("""
            INSERT INTO items_usuarios_tb (id_user,id_item,cantidad)
            VALUES (?,?,?)
        """,(id_user,id_item,cantidad))

    conn.commit()
    conn.close()
    return True

def delete_user(id_user):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(f"""
        DELETE FROM usuarios_tb
        WHERE id_user = {id_user}
    """)
    ret = cursor.rowcount
    conn.commit()
    conn.close()
    return bool(ret)
def delete_item(id_item):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(f"SELECT 1 FROM items_tb WHERE id_item = {id_item};")
    existe = cursor.fetchone()
    if not existe:
        print(f"[ERROR DB] No existe el item con el id: {id_item}")
        return False
    cursor.execute(f"""
        DELETE FROM items_tb
        WHERE id_item = {id_item}
    """)    
    conn.commit()
    conn.close()
    return True
def delete_item_user(id_user,id_item):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("SELECT 1 FROM items_usuarios_tb WHERE id_item = ? AND id_user = ?",(id_item,id_user))
    existe = cursor.fetchone()
    if not existe:
        print("[ERROR DB] No existe el item asociado con el usuario")
        return False
    cursor.execute("DELETE FROM items_usuarios_tb WHERE id_item = ? AND id_user = ?",(id_item,id_user))
    conn.commit()
    conn.close()

    

def update_perfil(id_user,**datos):
    columnas_validas = {
        "nombre","username","rol",
        "orientacion_sexual","genero",
        "ubicacion","edad"
    }

    for col in datos.keys():
        if col not in columnas_validas:
            print(f"[ERROR BD] Columna invalida: {col}")
            return False
    
    if not datos:
        print("[ERROR BD] No se enviaron datos para actualizar")
        return False
    
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    try:
        columnas = ", ".join([f"{col} = ?" for col in datos.keys()])
        valores = list(datos.values())
        valores.append(id_user)

        instruccion = f"""
            UPDATE perfiles_tb
            SET {columnas}
            WHERE id_user = ?
        """

        cursor.execute(instruccion,valores)
        conn.commit()
        return True
    
    except Exception as e:
        print("[ERROR BD]",e)
        conn.rollback()
        return False
    
    finally:
        conn.close()
def update_item(id_item,**datos):
    columnas_validas = {"nombre","precio","imagen","descripcion","mensaje"}
    if not datos:
        print("[ERROR BD] No se enviaron datos para actualizar")
        return False
    
    for col in datos.keys():
        if col not in columnas_validas:
            print(f"[ERROR BD] Columna no valida: {col}")
            return False
    
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        columnas = ", ".join([f"{col} = ?" for col in datos.keys()])
        valores = list(datos.values())
        valores.append(id_item)

        instruccion=f"""
            UPDATE items_tb
            SET {columnas}
            where id_item = ?
        """
        cursor.execute(instruccion,valores)
        conn.commit()
    
        if cursor.rowcount == 0:
            print("[ERROR BD] No se encontró un item con ese id")
            return False
        
        return True
    except Exception as e:
        print(f"[ERROR BD] Error al actualizar item: {e}")
        return False
    
    finally:
        conn.close()
def update_saldo(id_user,saldo=-1):
    if saldo == -1:
        print("[ERROR BD] No se proporciono un saldo valido")
        return False
    
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    try:
        instruccion = f"""
            UPDATE usuarios_tb
            SET saldo = ?
            WHERE id_user = ?
        """
        cursor.execute(instruccion,(saldo,id_user))
        if cursor.rowcount == 0:
            print("[ERROR BD] No existe un usuario con ese id_user")
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR BD] {e}")
        conn.close()
        return False
def update_cantidad(user_id,item_id,cantidad=-1):
    if cantidad == -1:
        print("[ERROR BD] No se proporciono una cantidad valida")
        return False
    
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    try:
        instruccion = f"""
            UPDATE items_usuarios_tb
            SET cantidad = ?
            WHERE id_user = ? AND id_item = ?
        """
        cursor.execute(instruccion,(cantidad,user_id,item_id))
        if cursor.rowcount == 0:
            print("[ERROR BD] No existe una relación con ese id_user e id_item")
            conn.close()
            return False
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR BD] {e}")
        conn.close()
        return False
    
def get_campo_usuario(id_user,columna):
    columnas_validas = {
        "nombre","username","rol",
        "orientacion_sexual","genero",
        "ubicacion","edad","saldo","id_user"
    }
    
    if columna not in columnas_validas:
        print(f"[ERROR DB] Tipo de columna no reconocida: {columna}")
        return None
    
    tabla = "perfiles_tb"
    if columna == "saldo":
        tabla = "usuarios_tb"
    
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    instruccion=f"SELECT {columna} FROM {tabla} WHERE id_user = ?"
    cursor.execute(instruccion,(id_user,))
    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return None

    return resultado[0]
def get_campo_item(id_item,columna):
    columnas_validas = {"id_item","nombre","precio","imagen","descripcion","mensaje"}

    if columna not in columnas_validas:
        print(f"[ERROR BD] Tipo de columna no reconocida: {columna}")
        return None

    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    instruccion = f"SELECT {columna} from items_tb WHERE id_item = ?"
    cursor.execute(instruccion,(id_item,))
    resultado = cursor.fetchone()

    if resultado is None:
        return None
    
    conn.commit()
    conn.close()
    return resultado[0]
def get_cantidad_item_inventario(id_user,id_item):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    instruccion = f"SELECT cantidad from items_usuarios_tb WHERE id_item = ? AND id_user = ?"
    cursor.execute(instruccion,(id_item,id_user))
    resultado = cursor.fetchone()

    if resultado is None:
        return 0
    
    conn.commit()
    conn.close()
    return resultado[0]

def get_items(id_user):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    instruccion = f"""
        SELECT
            items_tb.id_item,
            items_tb.nombre,
            items_tb.precio,
            items_tb.imagen,
            items_usuarios_tb.cantidad
        FROM items_usuarios_tb
        INNER JOIN items_tb
            ON items_tb.id_item = items_usuarios_tb.id_item
        WHERE items_usuarios_tb.id_user = ?
    """
    cursor.execute(instruccion,(id_user,))
    filas = cursor.fetchall()

    items = []
    for fila in filas:
        items.append({
            "id_item": fila[0],
            "nombre": fila[1],
            "precio":fila[2],
            "imagen":fila[3],
            "cantidad":fila[4]
        })

    conn.close()
    return items
def get_id_user(username):    
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    try:
        cursor.execute("""
            SELECT id_user
            FROM perfiles_tb
            WHERE username = ?
        """,(username,))

        resultado = cursor.fetchone()

        conn.close()
        if resultado:
            return resultado[0]

        return None
    except Exception as e:
        print(f"[ERROR BD] Error get_id_item:{e}")
        conn.close()
        return False
def get_id_item(nombre):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    nombre = to_plain_text(nombre,True).capitalize()
    print(nombre)
    try:
        cursor.execute("""
            SELECT id_item
            FROM items_tb
            WHERE nombre = ?
        """,(nombre,))

        resultado = cursor.fetchone()

        conn.close()
        if resultado:
            return resultado[0]

        return None
    except Exception as e:
        print(f"[ERROR BD] Error get_id_item:{e}")
        conn.close()
        return False
def dar_puntos(id_user,cantidad):
    cantidad_actual = get_campo_usuario(id_user,"saldo")
    if cantidad_actual == None or cantidad_actual == False:
        cantidad_actual = 0
    cantidad_actualizada = cantidad_actual + cantidad
    return update_saldo(id_user,cantidad_actualizada)
def quitar_puntos(id_user,cantidad):
    return dar_puntos(id_user,-cantidad)
    print
def normalizar_nombre(first_name:str,last_name:str = "") -> str:
    nombre_completo = f"{to_plain_text(first_name) or ''} {to_plain_text(last_name) or ''}".strip()
    nombre_completo = re.sub(r'[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñÜü ]+', '', nombre_completo)
    nombre_completo = unicodedata.normalize("NFKD",nombre_completo)
    nombre_completo = ''.join(
        c for c in nombre_completo
        if not unicodedata.combining(c)
    )
    nombre_completo = re.sub(r'\s+', ' ', nombre_completo).strip().lower()
    return nombre_completo
def to_plain_text(s:str,keep_space:bool = False) -> str:
    out_chars = []
    try:
        for ch in s:
            # 1) Normaliza compuestos (NFKD separa diacríticos)
            ch_nfd = unicodedata.normalize("NFKD", ch)

            # Recorremos la secuencia normalizada (por si hay letras + marcas)
            for ch2 in ch_nfd:
                cat = unicodedata.category(ch2)

                # Ignorar marcas combinantes (diacríticos) y control/format invisibles
                if cat.startswith("M"):  # Mark (combining)
                    continue
                if cat in ("Cc", "Cf"):  # Control / Format
                    continue

                # Si es ASCII alfanumérico lo aceptamos tal cual
                if '0' <= ch2 <= '9' or 'A' <= ch2 <= 'Z' or 'a' <= ch2 <= 'z':
                    out_chars.append(ch2)
                    continue

                # Tratamiento por nombre Unicode: muchas letras "fancy" incluyen
                # "LATIN ... LETTER <X>" en su nombre (p. ej. MATHEMATICAL BOLD CAPITAL A,
                # CIRCLED LATIN SMALL LETTER A, etc.). Intentamos extraer la letra base.
                try:
                    name = unicodedata.name(ch2)
                except ValueError:
                    name = ""

                if "LATIN" in name and "LETTER" in name:
                    # Buscamos la última token después de 'LETTER ' (p.ej. 'LATIN CAPITAL LETTER A' -> 'A')
                    m = re.search(r"LETTER\s+([A-Z]+[A-Z0-9]*)$", name)
                    if m:
                        token = m.group(1)
                        # token puede ser 'AE' o similar; tomamos cada letra por separado si corresponde
                        # pero normalmente es una sola letra A..Z
                        for c in token:
                            if 'A' <= c <= 'Z':
                                out_chars.append(c)
                        continue

                # Algunos símbolos son separadores (espacios invisibles) -> tratarlos como espacio
                if cat.startswith("Z"):  # Separator (space, line sep, paragraph sep)
                    out_chars.append(" ")
                    continue

                # Otros caracteres decorativos (p. ej. dingbats, ornamentos) los ignoramos.
                # Si quisieras conservar dígitos de otros scripts, podrías mapearlos aquí.
                # Por defecto: ignorar.
                # continue -> implica no añadir nada

        # unir, normalizar espacios, limpiar no-alphanum según preferencia
        text = "".join(out_chars)

        if keep_space:
            # Normalizar múltiples espacios a uno y recortar
            text = re.sub(r"\s+", " ", text).strip()
            # Ahora eliminar cualquier carácter que no sea ASCII alfanumérico o espacio
            text = re.sub(r"[^0-9A-Za-z ]+", "", text)
        else:
            # Eliminar todo excepto ASCII alfanumérico
            text = re.sub(r"[^0-9A-Za-z]+", "", text)

        return reemplazar_acentos(text.lower())
    except TypeError:
        return ""
def reemplazar_acentos(cadena):
    reemplazos = (
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
        ("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U")
    )
    for acentuada, normalizada in reemplazos:
        cadena = cadena.replace(acentuada, normalizada)
    return cadena  