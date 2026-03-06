import sqlite3

from sqlgestion import update_item,update_saldo

def agregar_columna_mensaje(db_path="usuarios.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Revisar columnas actuales
    cursor.execute("PRAGMA table_info(items_tb)")
    columnas = [col[1] for col in cursor.fetchall()]

    # 2. Agregar la columna solo si no existe
    if "mensaje" not in columnas:
        try:
            cursor.execute("ALTER TABLE items_tb ADD COLUMN mensaje TEXT")
            print("✔️ Columna 'mensaje' agregada correctamente.")
        except Exception as e:
            print("❌ Error al agregar la columna:", e)
    else:
        print("ℹ️ La columna 'mensaje' ya existe. No se realizó ningún cambio.")

    conn.commit()
    conn.close()


# Ejecutar la función
#update_item(1,mensaje="😈 {sender_username} le ha puesto un collar muy bonito a {receptor_username} 😍\n ¡Qué envidiaaa!")
#update_item(2,mensaje="😱 {sender_username} ha azotado con un látigo a {receptor_username} \n ... Eso va a dejar marca 🫦")
#update_item(3,mensaje="🤩 {sender_username} está adiestrando a {receptor_username} con su fusta favorita 😈\n ¿Porqué parece que {receptor_username} lo disfruta?... 🫦")
#update_item(4,mensaje="❤ {sender_username} le ha regalado a {receptor_username} una galleta 🍪\n Parece que se ha portado muy bien 🤤")
#update_item(5,mensaje="🤏 {sender_username} Le ha puesto una bola mordaza a {receptor_username}\n Que bien te ves sin poder hablar 😖")
#update_item(6,mensaje="😈 {sender_username} ha decidido modelarle algo de su lencería sexy a {receptor_username}\n Le queda muy bien, aunque no esperaba que {sender_username} hiciera eso frente a todos 👁👄👁")

update_saldo(1174798556,1610+5000)
