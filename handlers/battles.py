"""
Battle/Combat system handler for PiBot.

Implements D&D-style battle mechanics with:
- Health points (HP)
- Dice rolls for damage
- Turn-based combat
- Betting on battles
"""

import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from src.database.database import (
    get_campo_usuario, update_saldo, dar_puntos, quitar_puntos,
    _get_connection
)


# ==================== BATTLE OPERATIONS ====================

def crear_combate(id_atacante: int, id_defensor: int, username_atacante: str,
                  username_defensor: str, apuesta: int) -> int:
    """
    Create a new battle in the database.
    
    Args:
        id_atacante: Attacker's Telegram ID
        id_defensor: Defender's Telegram ID
        username_atacante: Attacker's username
        username_defensor: Defender's username
        apuesta: Bet amount in PiPesos
    
    Returns:
        Combat ID or -1 if failed
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        cursor.execute("""
            INSERT INTO combates_tb 
            (id_atacante, id_defensor, username_atacante, username_defensor, apuesta, hp_atacante, hp_defensor)
            VALUES (?, ?, ?, ?, ?, 20, 20)
        """, (id_atacante, id_defensor, username_atacante, username_defensor, apuesta))
        
        conn.commit()
        combat_id = cursor.lastrowid
        conn.close()
        return combat_id
    except Exception as e:
        print(f"[ERROR DB] Failed to create battle: {e}")
        return -1


def get_combate_activo(id_user: int) -> dict:
    """
    Get active combat for a user (as attacker or defender).
    
    Args:
        id_user: User's Telegram ID
    
    Returns:
        Combat dictionary or None if no active combat
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM combates_tb 
            WHERE (id_atacante = ? OR id_defensor = ?) 
            AND estado = 'activo'
            LIMIT 1
        """, (id_user, id_user))
        
        resultado = cursor.fetchone()
        conn.close()
        
        if not resultado:
            return None
        
        # Convert tuple to dict
        return {
            'id_combate': resultado[0],
            'id_atacante': resultado[1],
            'id_defensor': resultado[2],
            'username_atacante': resultado[3],
            'username_defensor': resultado[4],
            'apuesta': resultado[5],
            'hp_atacante': resultado[6],
            'hp_defensor': resultado[7],
            'turno': resultado[8],
            'es_turno_atacante': resultado[9],
            'estado': resultado[10],
            'ganador': resultado[11]
        }
    except Exception as e:
        print(f"[ERROR DB] Error getting active combat: {e}")
        return None


def actualizar_combate(id_combate: int, **datos) -> bool:
    """
    Update combat fields.
    
    Args:
        id_combate: Combat ID
        **datos: Fields to update
    
    Returns:
        True if successful, False otherwise
    """
    columnas_validas = {
        "hp_atacante", "hp_defensor", "turno", "es_turno_atacante", "estado", "ganador"
    }
    
    if not datos:
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
        valores = list(datos.values()) + [id_combate]
        
        cursor.execute(f"UPDATE combates_tb SET {columnas} WHERE id_combate = ?", valores)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR DB] Error updating combat: {e}")
        return False


def terminar_combate(id_combate: int, id_ganador: int) -> bool:
    """
    End a combat and process rewards.
    
    Args:
        id_combate: Combat ID
        id_ganador: Winner's user ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        combate = get_combate_by_id(id_combate)
        if not combate:
            return False
        
        # Update combat status
        actualizar_combate(
            id_combate,
            estado='finalizado',
            ganador=id_ganador
        )
        
        # Transfer bet to winner
        if combate['apuesta'] > 0:
            dar_puntos(id_ganador, combate['apuesta'] * 2)
        
        return True
    except Exception as e:
        print(f"[ERROR DB] Error ending combat: {e}")
        return False


def get_combate_by_id(id_combate: int) -> dict:
    """
    Get combat by ID.
    
    Args:
        id_combate: Combat ID
    
    Returns:
        Combat dictionary or None if not found
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM combates_tb WHERE id_combate = ?", (id_combate,))
        resultado = cursor.fetchone()
        conn.close()
        
        if not resultado:
            return None
        
        return {
            'id_combate': resultado[0],
            'id_atacante': resultado[1],
            'id_defensor': resultado[2],
            'username_atacante': resultado[3],
            'username_defensor': resultado[4],
            'apuesta': resultado[5],
            'hp_atacante': resultado[6],
            'hp_defensor': resultado[7],
            'turno': resultado[8],
            'es_turno_atacante': resultado[9],
            'estado': resultado[10],
            'ganador': resultado[11]
        }
    except Exception as e:
        print(f"[ERROR DB] Error getting combat by ID: {e}")
        return None


# ==================== BATTLE COMMANDS ====================

async def lucha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start a battle with another user.
    Syntax: /lucha [@username] [cantidad]
    
    Args:
        update: Telegram update
        context: Command context
    """
    sender = update.effective_user
    chat_id = update.effective_chat.id
    
    # Check if sender already in combat
    combate_activo = get_combate_activo(sender.id)
    if combate_activo:
        await update.message.reply_text(
            "⚔️ Ya estás en un combate activo.\n"
            "Espera a que termine antes de empezar otro."
        )
        return
    
    # Parse arguments: /lucha [@usuario] [cantidad]
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Uso: /lucha @usuario cantidad\n"
            "Ejemplo: /lucha @juan 50\n\n"
            "⚔️ Empezarás con 20 HP\n"
            "🎲 Cada turno lanzarás un dado para infliar daño\n"
            "💰 El ganador se queda con la apuesta"
        )
        return
    
    # Get opponent username
    opponent_username = context.args[0].replace("@", "")
    
    # Get opponent ID
    from src.database.database import get_id_user
    opponent_id = get_id_user(opponent_username)
    
    if not opponent_id:
        await update.message.reply_text(f"❌ No encontré a @{opponent_username}")
        return
    
    if opponent_id == sender.id:
        await update.message.reply_text("❌ No puedes luchar contra ti mismo")
        return
    
    # Get bet amount
    try:
        apuesta = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ La apuesta debe ser un número")
        return
    
    if apuesta <= 0:
        await update.message.reply_text("❌ La apuesta debe ser mayor a 0")
        return
    
    # Check balance
    saldo_atacante = get_campo_usuario(sender.id, "saldo") or 0
    saldo_defensor = get_campo_usuario(opponent_id, "saldo") or 0
    
    if saldo_atacante < apuesta:
        await update.message.reply_text(
            f"❌ No tienes suficientes PiPesos\n"
            f"Tienes: {saldo_atacante} | Necesitas: {apuesta}"
        )
        return
    
    if saldo_defensor < apuesta:
        await update.message.reply_text(
            f"❌ @{opponent_username} no tiene suficientes PiPesos para apostar\n"
            f"Tiene: {saldo_defensor} | Necesita: {apuesta}"
        )
        return
    
    # Create combat
    combat_id = crear_combate(
        sender.id, opponent_id,
        sender.username or f"Usuario{sender.id}",
        opponent_username,
        apuesta
    )
    
    if combat_id == -1:
        await update.message.reply_text("❌ Error al crear el combate")
        return
    
    # Deduct bet from both players
    quitar_puntos(sender.id, apuesta)
    quitar_puntos(opponent_id, apuesta)
    
    # Send challenge message
    mensaje = (
        f"⚔️ **¡COMBATE INICIADO!**\n\n"
        f"🥊 {sender.username} ⚔️ @{opponent_username}\n"
        f"❤️ HP: 20 vs 20\n"
        f"💰 Apuesta: {apuesta} PiPesos cada uno\n\n"
        f"Turno actual: {sender.username}\n"
        f"Usa /ataque para atacar al oponente"
    )
    
    await context.bot.send_message(chat_id, mensaje, parse_mode='Markdown')


async def ataque(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Perform an attack in an active battle.
    Rolls a d12 for damage.
    
    Args:
        update: Telegram update
        context: Command context
    """
    sender = update.effective_user
    chat_id = update.effective_chat.id
    
    # Get active combat
    combate = get_combate_activo(sender.id)
    
    if not combate:
        await update.message.reply_text(
            "❌ No tienes un combat activo\n"
            "Usa /lucha @usuario cantidad para iniciar uno"
        )
        return
    
    # Check if it's the sender's turn
    es_turno = (
        (combate['es_turno_atacante'] == 1 and combate['id_atacante'] == sender.id) or
        (combate['es_turno_atacante'] == 0 and combate['id_defensor'] == sender.id)
    )
    
    if not es_turno:
        atacante_nombre = combate['username_atacante'] if combate['es_turno_atacante'] else combate['username_defensor']
        await update.message.reply_text(f"⏳ Es el turno de {atacante_nombre}")
        return
    
    # Roll d12 for damage
    daño = random.randint(1, 12)
    
    # Determine attacker and defender
    if combate['id_atacante'] == sender.id:
        hp_defensor = combate['hp_defensor'] - daño
        hp_atacante = combate['hp_atacante']
        atacante_nombre = combate['username_atacante']
        defensor_nombre = combate['username_defensor']
    else:
        hp_atacante = combate['hp_atacante'] - daño
        hp_defensor = combate['hp_defensor']
        atacante_nombre = combate['username_defensor']
        defensor_nombre = combate['username_atacante']
    
    # Ensure HP doesn't go below 0
    hp_atacante = max(0, hp_atacante)
    hp_defensor = max(0, hp_defensor)
    
    # Update combat
    actualizar_combate(
        combate['id_combate'],
        hp_atacante=hp_atacante,
        hp_defensor=hp_defensor,
        es_turno_atacante=1 if combate['es_turno_atacante'] == 0 else 0,
        turno=combate['turno'] + 1
    )
    
    # Check if combat is over
    if hp_defensor <= 0:
        # Attacker wins
        id_ganador = sender.id
        terminar_combate(combate['id_combate'], id_ganador)
        
        mensaje = (
            f"🎉 **¡COMBATE FINALIZADO!**\n\n"
            f"🏆 Ganador: {atacante_nombre}\n"
            f"💀 Perdedor: {defensor_nombre}\n\n"
            f"🎲 Turno {combate['turno']}: {atacante_nombre} atacó por {daño} de daño\n"
            f"💰 Ganador recibió {combate['apuesta'] * 2} PiPesos"
        )
    else:
        # Combat continues
        turno_actual = "Turno"
        siguiente_atacante = defensor_nombre if combate['es_turno_atacante'] == 1 else atacante_nombre
        
        mensaje = (
            f"⚔️ **{siguiente_atacante} ataca!**\n\n"
            f"{atacante_nombre}: ❤️ {hp_atacante}\n"
            f"{defensor_nombre}: ❤️ {hp_defensor}\n\n"
            f"🎲 {atacante_nombre} lanzó {daño} de daño\n"
            f"📊 {siguiente_atacante}, es tu turno. Usa /ataque"
        )
    
    await context.bot.send_message(chat_id, mensaje, parse_mode='Markdown')
