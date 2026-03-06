import asyncio,random
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from handlers.general import get_receptor
from sqlgestion import normalizar_nombre,get_campo_usuario,insert_user,dar_puntos,quitar_puntos,update_perfil
from config import obtener_temas_por_comunidad

# === BASE DE DATOS EN MEMORIA ===
active_bets = {}
robar_usuarios = {}
juego = {}

# === CREAR APUESTA ===
async def apostar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    CHAT_IDS = obtener_temas_por_comunidad(update.effective_chat.id)

    thread_id = update.message.message_thread_id
    user = update.effective_user
    
    if thread_id != CHAT_IDS["theme_juegosYcasino"]:
        await update.message.reply_text("⚠️ Este comando solo está permitido en el tema Juegos y Casino.")
        return

    # 📌 Validar parámetros
    if len(context.args) < 1:
        await update.message.reply_text("Uso: /apostar <cantidad>")
        return

    try:
        cantidad = int(context.args[0])
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ La cantidad debe ser un número mayor que 0.")
        return

    #Verificar si ya hay una apuesta activa
    if thread_id in active_bets:
        await update.message.reply_text("⚠️ Ya hay una apuesta activa en este tema.")
        return

    # 📌 Verificar si el usuario existe y tiene saldo suficiente
    user_id = user.id
    user_username = user.username
    user_nombre = normalizar_nombre(user.first_name,user.last_name)

    if get_campo_usuario(user_id,"id_user"):
        user_saldo = get_campo_usuario(user_id,"saldo")
    else:
        insert_user(user_id,0,user_username,user_nombre)
        user_saldo = 0
    
    if user_saldo < cantidad:
        await update.message.reply_text(f"💸 Saldo insuficiente. Tu saldo es de {user_saldo} PiPesos.")
        return

    # 📌 Guardar apuesta inicial en memoria
    active_bets[thread_id] = {
        "apostador_id": user_id,
        "apostador_username": user_username or user_nombre,
        "rival_id": None,
        "rival_username": None,
        "cantidad": cantidad,
        "dados": {"apostador": None, "rival": None},
        "activa": True
    }

    await update.message.reply_text(
        f"🎲 {user_username or user_nombre} ha creado una apuesta de {cantidad} PiPesos.\n"
        "Cualquier jugador puede escribir /aceptar para unirse en los próximos 60 segundos."
    )

    # 📌 Auto-cancelación en 60 segundos
    async def auto_cancel():
        await asyncio.sleep(60)
        bet = active_bets.get(thread_id)
        if bet and bet["activa"] and bet["rival_id"] is None:
            del active_bets[thread_id]
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⏳ Tiempo agotado. La apuesta fue cancelada automáticamente.",
                message_thread_id=thread_id
            )

    asyncio.create_task(auto_cancel())

# === ACEPTAR APUESTA ===
async def aceptar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    CHAT_IDS = obtener_temas_por_comunidad(update.effective_chat.id)
    
    thread_id = update.message.message_thread_id
    user = update.effective_user
    
    bet = active_bets.get(thread_id)
    if not bet:
        await update.message.reply_text("⚠️ No hay apuestas activas para aceptar en este tema.")
        return

    if bet["rival_id"] is not None:
        await update.message.reply_text("⚠️ Esta apuesta ya fue aceptada por otro jugador.")
        return

    if user.id == bet["apostador_id"]:
        await update.message.reply_text("⚠️ No puedes aceptar tu propia apuesta.")
        return

    # 📌 Verificar si el usuario existe en el sistema
    user_id = user.id
    user_username = user.username
    user_nombre = normalizar_nombre(user.first_name,user.last_name)
    
    if get_campo_usuario(user_id,"id_user"):
        user_saldo = get_campo_usuario(user_id,"saldo")
    else:
        user_saldo = 0
        insert_user(user_id,user_saldo,user_username,user_nombre)

    if user_saldo < bet["cantidad"]:
        await update.message.reply_text(f"💸 Saldo insuficiente. Tu saldo es {user_saldo} PiPesos.")
        return

    bet["rival_id"] = user_id
    bet["rival_username"] = user_username or user_nombre

    await update.message.reply_text(
        f"✅ {user_username or user_nombre} ha aceptado la apuesta de "
        f"{bet['apostador_username']}.\n\n🎲 ¡Ambos deben lanzar el dado para continuar!"
    )

# === CANCELAR APUESTA ===
async def cancelar_apuesta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    thread_id = update.message.message_thread_id
    user = update.effective_user
    
    bet = active_bets.get(thread_id)
    if not bet:
        await update.message.reply_text("⚠️ No hay apuesta activa para cancelar en este tema.")
        return

    # 📌 Solo el creador puede cancelar
    if user.id != bet["apostador_id"]:
        await update.message.reply_text("⚠️ Solo quien creó la apuesta puede cancelarla.")
        return

    # ✅ Cancelar apuesta
    del active_bets[thread_id]
    await update.message.reply_text(
        f"❌ {user.username or user.first_name} canceló la apuesta."
    )

# === DETECTAR DADOS ===
async def detectar_dado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    msg = update.message
    if not msg or not msg.dice:
        return  # ignorar mensajes que no sean dados

    thread_id = msg.message_thread_id
    bet = active_bets.get(thread_id)
    if not bet:
        return  # no hay apuesta activa

    user = msg.from_user

    if user.id == bet["apostador_id"]:
        jugador = "apostador"
    elif user.id == bet["rival_id"]:
        jugador = "rival"
    else:
        return  # no es parte de la apuesta
    
    if bet["dados"][jugador] is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Ya haz lanzado el dado, no puedes volver a lanzar",
            message_thread_id=thread_id
        )
        return
    
    valor = msg.dice.value
    bet["dados"][jugador] = valor

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🎲 @{user.username or user.first_name} ha lanzado el dado y sacó {valor}",
        message_thread_id=thread_id
    )

    # Si ambos ya lanzaron, anunciar ganador
    if bet["dados"]["apostador"] is not None and bet["dados"]["rival"] is not None:
        ap = bet["dados"]["apostador"]
        rv = bet["dados"]["rival"]

        apostador_id = bet["apostador_id"]
        rival_id = bet["rival_id"]
        cantidad = bet["cantidad"]

        if ap > rv:
            ganador = bet["apostador_username"]
            resultado = f"🏆 *{ganador}* gana la apuesta de {cantidad} PiPesos!"
            dar_puntos(apostador_id, cantidad)
            quitar_puntos(rival_id, cantidad)

        elif rv > ap:
            ganador = bet["rival_username"]
            resultado = f"🏆 *{ganador}* gana la apuesta de {cantidad} PiPesos!"
            dar_puntos(rival_id, cantidad)
            quitar_puntos(apostador_id, cantidad)

        else:
            resultado = "🤝 ¡Empate! Nadie gana ni pierde."

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=resultado,
            message_thread_id=thread_id
        )

        # ✅ Finalizar apuesta
        del active_bets[thread_id]

async def jugar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_IDS = obtener_temas_por_comunidad(update.effective_chat.id)

    thread_id = update.message.message_thread_id
    user = update.effective_user
    user_id = user.id
    
    tmp_user_username = user.username
    tmp_user_nombre = normalizar_nombre(user.first_name,user.last_name)
    sql_user_username = get_campo_usuario(user_id,"username")
    sql_user_nombre = get_campo_usuario(user_id,"nombre")

    if get_campo_usuario(user_id,"id_user") is None:
        insert_user(user_id,0,tmp_user_username,tmp_user_nombre)

    if tmp_user_nombre != sql_user_nombre or tmp_user_username != sql_user_username:
        update_perfil(user_id,username=tmp_user_username,nombre=tmp_user_nombre)

    sql_user_username = tmp_user_username
    sql_user_nombre = tmp_user_nombre

    if thread_id != CHAT_IDS["theme_juegosYcasino"]:
        await update.message.reply_text("⚠️ Este comando solo está permitido en el tema Juegos y Casino.")
        return

    hoy = datetime.now().strftime("%Y-%m-%d")

    juego_ejecutado = juego.get(user_id)
    if  juego_ejecutado is None:
        juego[user_id] = {
            "fecha":hoy,
            "veces":0
        }
        juego_ejecutado = juego.get(user_id)
    tmp_fecha = juego_ejecutado["fecha"]
    tmp_veces = juego_ejecutado["veces"]
    
    if tmp_veces >= 5:
        await update.message.reply_text(
            f"⚠️ Ya has jugado 5 veces hoy. Inténtalo de nuevo mañana.",
            message_thread_id=thread_id
        )
        return
    
    juego_ejecutado["veces"] = tmp_veces + 1

    dice_message = await context.bot.send_dice(
        chat_id=update.effective_chat.id,
        emoji="🎲",
        message_thread_id=thread_id
    )
    valor = dice_message.dice.value
    if valor == 6 or valor == 1:
        dar_puntos(user_id, 50)
        resultado = f"🎉 ¡Ganaste! sacaste {valor} 🎲\n💰 Se te acreditaron 50 PiPesos."
    else:
        resultado = f"😔 Sacaste {valor}, perdiste."

    nuevo_saldo = get_campo_usuario(user_id,"saldo")

    await update.message.reply_text(
        f"{resultado}\nSaldo actual: {nuevo_saldo} PiPesos\n"
        f"🔄 Veces jugadas hoy: {tmp_veces+1}/5",
        message_thread_id=thread_id
    )

async def robar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /robar @Usuario - Solo válido con @Usuario, no con reply."""
    CHAT_IDS = obtener_temas_por_comunidad(update.effective_chat.id)
    
    try:
        thread_id = update.message.message_thread_id
    except ArithmeticError or TypeError as e:
        hora = datetime.now().time()
        print(f"No ha sido posible identificar el tema, {e}\nError a las: {hora.hour}:{hora.minute}")
        del hora
        return
    
    robber_user = update.effective_user
    robbed_user = None
    sql_robber_username = get_campo_usuario(robber_user.id,"username")
    tmp_robber_username = robber_user.username
    sql_robber_nombre = get_campo_usuario(robber_user.id,"nombre")
    tmp_robber_nombre = normalizar_nombre(robber_user.first_name,robber_user.last_name)
    
    if get_campo_usuario(robber_user.id,"id_user") is None:
        insert_user(robber_user.id,0,tmp_robber_username,tmp_robber_nombre)
        sql_robber_nombre = tmp_robber_nombre
        sql_robber_username = tmp_robber_username

    if tmp_robber_username != sql_robber_username or tmp_robber_nombre != sql_robber_nombre:
        update_perfil(robber_user.id,username=tmp_robber_username,nombre=tmp_robber_nombre)
        sql_robber_nombre = tmp_robber_nombre
        sql_robber_username = tmp_robber_username
    
    # 1) Solo en el tema Juegos y Casino
    if thread_id != CHAT_IDS["theme_juegosYcasino"]:
        await update.message.reply_text("⚠️ Este comando solo se puede usar en el tema Juegos y Casino.")
        return
    
    robbed_user = await get_receptor(update,context,1)
    
    if robbed_user is None or robbed_user is False:
        await update.message.reply_text("⚠️ No ha sido posible encontrar al usuario.")
        return    
    
    robber_id = robber_user.id
    robbed_id = robbed_user.id
    robbed_username = robbed_user.username
    
    # 4) Control de uso diario
    if robar_usuarios.get(robber_id) is None:
        robar_usuarios[robber_id] = 0

    if robar_usuarios.get(robber_id) >= 3:
        await update.message.reply_text("⚠️ Solo puedes usar /robar 3 vez al día.")
        return

    robar_usuarios[robber_id] = robar_usuarios[robber_id]+1 

    exito = random.choice([True, False, False])

    if exito:
        cantidad_robada = random.randint(1,100)
        saldo_robbed_user = get_campo_usuario(robbed_user.id,"saldo")
        if cantidad_robada > saldo_robbed_user :
            cantidad_robada = saldo_robbed_user
        
        quitar_puntos(robbed_id,cantidad_robada)
        dar_puntos(robber_id,cantidad_robada)
        await update.message.reply_text(f"🎉 {sql_robber_username} logró robar a {robbed_username} exitosamente {cantidad_robada} PiPesos")
    else:
        await update.message.reply_text(f"💨 {sql_robber_username} intentó robar a {robbed_username}, pero falló.")