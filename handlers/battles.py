"""
Battle/Combat system handler for PiBot.

Refactored battle system with:
- Challenge phase (/lucha [@usuario] [cantidad])
- 60-second acceptance phase (/aceptar lucha)
- Turn-based combat with dice rolls
- Dice emoji as damage system
"""

import asyncio
import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from src.database.database import (
    get_campo_usuario, update_saldo, dar_puntos, quitar_puntos,
    _get_connection
)


# ==================== IN-MEMORY BATTLE STATE ====================
# Pending challenges: {user_id: {"opponent_id": id, "opponent_username": username, "apuesta": amount, "timestamp": datetime}}
pending_challenges = {}

# ==================== IN-MEMORY BATTLE STATE ====================
# Pending challenges: {user_id: {"opponent_id": id, "opponent_username": username, "apuesta": amount, "timestamp": datetime}}
pending_challenges = {}


# ==================== DATABASE OPERATIONS ====================

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
            'ganador': resultado[11],
            'fecha_inicio': resultado[12]
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
            'ganador': resultado[11],
            'fecha_inicio': resultado[12]
        }
    except Exception as e:
        print(f"[ERROR DB] Error getting combat by ID: {e}")
        return None


# ==================== BATTLE COMMANDS ====================

async def lucha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start a battle challenge with another user.
    Syntax: /lucha [@username] [cantidad]
    
    The opponent has 60 seconds to accept with /aceptar lucha
    """
    sender = update.effective_user
    sender_username = sender.username or f"Usuario{sender.id}"
    
    # Check if sender already has a pending challenge or active combat
    if sender.id in pending_challenges:
        await update.message.reply_text(
            "⚔️ Ya tienes un desafío pendiente.\n"
            "Espera a que sea aceptado o rechazado."
        )
        return
    
    if get_combate_activo(sender.id):
        await update.message.reply_text(
            "⚔️ Ya estás en un combate activo.\n"
            "Termina el combate antes de retarme a otro."
        )
        return
    
    # Parse arguments
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "📋 Uso: /lucha @usuario cantidad\n"
            "Ejemplo: /lucha @juan 50\n\n"
            "⚔️ Cómo funciona:\n"
            "1️⃣ Retar a alguien (tiene 60s para aceptar)\n"
            "2️⃣ Si acepta, inicia el combate\n"
            "3️⃣ Lanzan dados por turnos alternados\n"
            "4️⃣ Lanza el dado 🎲 (el resultado es el daño)\n"
            "5️⃣ Primero en llegar a 0 HP pierde\n"
            "💰 El ganador se queda con la apuesta doble"
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
        await update.message.reply_text("❌ No puedes retarte a ti mismo")
        return
    
    # Check if opponent already has a pending challenge or active combat
    if opponent_id in pending_challenges or get_combate_activo(opponent_id):
        await update.message.reply_text(
            f"❌ @{opponent_username} ya está en un combate o tiene un desafío pendiente"
        )
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
            f"❌ Saldo insuficiente\n"
            f"Tienes: {saldo_atacante} PiPesos | Necesitas: {apuesta}"
        )
        return
    
    if saldo_defensor < apuesta:
        await update.message.reply_text(
            f"❌ @{opponent_username} no tiene suficientes PiPesos\n"
            f"Tiene: {saldo_defensor} | Necesita: {apuesta}"
        )
        return
    
    # Deduct bet from both players
    quitar_puntos(sender.id, apuesta)
    quitar_puntos(opponent_id, apuesta)
    
    # Store challenge in memory
    pending_challenges[sender.id] = {
        "opponent_id": opponent_id,
        "opponent_username": opponent_username,
        "apuesta": apuesta,
        "timestamp": datetime.now()
    }
    
    # Send challenge message to opponent
    challenge_msg = (
        f"⚔️ **¡DESAFÍO DE LUCHA!**\n\n"
        f"🥊 {sender_username} te reta a batalla\n"
        f"💰 Apuesta: {apuesta} PiPesos para cada uno\n\n"
        f"⏱️ Tienes 60 segundos para aceptar\n"
        f"Escribe: /aceptarlucha"
    )
    
    await context.bot.send_message(
        chat_id=opponent_id,
        text=challenge_msg,
        parse_mode='Markdown'
    )
    
    await update.message.reply_text(
        f"✅ Desafío enviado a @{opponent_username}\n"
        f"Esperando su respuesta... ⏳"
    )
    
    # Setup 60-second timeout
    async def timeout_challenge():
        await asyncio.sleep(60)
        if sender.id in pending_challenges:
            # Challenge expired
            del pending_challenges[sender.id]
            
            # Return bet to both players
            dar_puntos(sender.id, apuesta)
            dar_puntos(opponent_id, apuesta)
            
            await context.bot.send_message(
                chat_id=opponent_id,
                text=f"⏱️ El desafío de {sender_username} expiró sin respuesta"
            )
            await context.bot.send_message(
                chat_id=sender.id,
                text=f"⏱️ @{opponent_username} no aceptó el desafío\n"
                f"Se devolvieron {apuesta} PiPesos"
            )
    
    asyncio.create_task(timeout_challenge())


async def aceptar_lucha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Accept a battle challenge.
    Syntax: /aceptarlucha
    """
    user = update.effective_user
    user_id = user.id
    user_username = user.username or f"Usuario{user_id}"
    
    # Check if there's a challenge for this user
    challenge = None
    challenger_id = None
    
    for chall_id, chall_data in pending_challenges.items():
        if chall_data["opponent_id"] == user_id:
            challenge = chall_data
            challenger_id = chall_id
            break
    
    if not challenge:
        await update.message.reply_text(
            "❌ No tienes ningún desafío pendiente\n"
            "Alguien debe retarte primero con /lucha"
        )
        return
    
    # Check timeout (60 seconds)
    time_elapsed = datetime.now() - challenge["timestamp"]
    if time_elapsed > timedelta(seconds=60):
        # Challenge expired
        if challenger_id in pending_challenges:
            del pending_challenges[challenger_id]
        
        await update.message.reply_text("⏱️ Este desafío ya expiró")
        return
    
    # Remove challenge from pending
    del pending_challenges[challenger_id]
    
    # Get challenger info
    challenger_username = get_campo_usuario(challenger_id, "username")
    if not challenger_username:
        challenger_username = f"Usuario{challenger_id}"
    
    apuesta = challenge["apuesta"]
    
    # Create combat
    combat_id = crear_combate(
        challenger_id, user_id,
        challenger_username,
        user_username,
        apuesta
    )
    
    if combat_id == -1:
        await update.message.reply_text("❌ Error al crear el combate")
        # Refund the bets
        dar_puntos(challenger_id, apuesta)
        dar_puntos(user_id, apuesta)
        return
    
    # Get combat details
    combate = get_combate_by_id(combat_id)
    
    # Start combat message
    start_msg = (
        f"⚔️ **¡COMBATE INICIADO!**\n\n"
        f"🥊 {combate['username_atacante']} vs {combate['username_defensor']}\n"
        f"❤️ HP: 20 vs 20\n"
        f"💰 Apuesta: {apuesta} PiPesos para cada jugador\n\n"
        f"📊 Primer turno: @{combate['username_atacante']}\n"
        f"🎲 Lanza el dado 🎲 para atacar"
    )
    
    # Send to both players
    await context.bot.send_message(
        chat_id=challenger_id,
        text=start_msg,
        parse_mode='Markdown'
    )
    await context.bot.send_message(
        chat_id=user_id,
        text=start_msg,
        parse_mode='Markdown'
    )
    
    await update.message.reply_text("✅ ¡Combate iniciado!")


async def dados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Attack with a dice roll. Triggered when user sends a dice emoji 🎲
    The dice result (1-6) is the damage dealt to the opponent.
    """
    sender = update.effective_user
    sender_id = sender.id
    sender_username = sender.username or f"Usuario{sender_id}"
    
    # Get active combat
    combate = get_combate_activo(sender_id)
    
    if not combate:
        # User sent a dice but not in combat - ignore silently
        return
    
    # Check if it's the sender's turn
    es_turno = (
        (combate['es_turno_atacante'] == 1 and combate['id_atacante'] == sender_id) or
        (combate['es_turno_atacante'] == 0 and combate['id_defensor'] == sender_id)
    )
    
    if not es_turno:
        turno_de = combate['username_atacante'] if combate['es_turno_atacante'] else combate['username_defensor']
        await update.message.reply_text(
            f"⏳ No es tu turno\n"
            f"Aguarda a que {turno_de} ataque"
        )
        return
    
    # Get damage from dice result (1-6)
    daño = update.message.dice.value
    
    # Determine attacker and defender based on current turn
    if combate['es_turno_atacante'] == 1:
        hp_defensor = combate['hp_defensor'] - daño
        hp_atacante = combate['hp_atacante']
        atacante_nombre = combate['username_atacante']
        defensor_nombre = combate['username_defensor']
        id_atacante_turno = combate['id_atacante']
        id_defensor_turno = combate['id_defensor']
    else:
        hp_atacante = combate['hp_atacante'] - daño
        hp_defensor = combate['hp_defensor']
        atacante_nombre = combate['username_defensor']
        defensor_nombre = combate['username_atacante']
        id_atacante_turno = combate['id_defensor']
        id_defensor_turno = combate['id_atacante']
    
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
        id_ganador = id_atacante_turno
        terminar_combate(combate['id_combate'], id_ganador)
        
        # Determine actual original roles for message
        if combate['es_turno_atacante'] == 1:
            ganador_name = combate['username_atacante']
            perdedor_name = combate['username_defensor']
        else:
            ganador_name = combate['username_defensor']
            perdedor_name = combate['username_atacante']
        
        fin_msg = (
            f"🎉 **¡COMBATE FINALIZADO!**\n\n"
            f"🏆 Ganador: {ganador_name}\n"
            f"💀 Perdedor: {perdedor_name}\n\n"
            f"🎲 Último turno: {atacante_nombre} lanzó {daño} de daño\n"
            f"❤️ {ganador_name}: {hp_atacante if id_ganador == combate['id_atacante'] else hp_defensor} HP\n"
            f"💀 {perdedor_name}: 0 HP\n\n"
            f"💰 Ganador recibió {combate['apuesta'] * 2} PiPesos"
        )
        
        await context.bot.send_message(
            chat_id=combate['id_atacante'],
            text=fin_msg,
            parse_mode='Markdown'
        )
        await context.bot.send_message(
            chat_id=combate['id_defensor'],
            text=fin_msg,
            parse_mode='Markdown'
        )
    else:
        # Combat continues - prepare next turn message
        siguiente_atacante = defensor_nombre if combate['es_turno_atacante'] == 1 else atacante_nombre
        siguiente_id = id_defensor_turno
        
        # Determine original roles for status display
        original_atacante = combate['username_atacante']
        original_defensor = combate['username_defensor']
        
        combate_msg = (
            f"⚔️ **COMBATE EN CURSO**\n\n"
            f"{original_atacante}: ❤️ {hp_atacante}\n"
            f"{original_defensor}: ❤️ {hp_defensor}\n\n"
            f"🎲 {atacante_nombre} lanzó {daño} de daño\n\n"
            f"📊 Turno de: @{siguiente_atacante}\n"
            f"Lanza el dado 🎲 para atacar"
        )
        
        # Send to both players
        await context.bot.send_message(
            chat_id=combate['id_atacante'],
            text=combate_msg,
            parse_mode='Markdown'
        )
        await context.bot.send_message(
            chat_id=combate['id_defensor'],
            text=combate_msg,
            parse_mode='Markdown'
        )
        
        # Notify whose turn it is with special mention
        await context.bot.send_message(
            chat_id=siguiente_id,
            text=f"🎲 Es tu turno, @{siguiente_atacante}. Lanza el dado para atacar"
        )


# Keep old 'ataque' function for compatibility (maps to 'dados')
ataque = dados
