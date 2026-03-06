import json
import os
from telegram import ChatPermissions, Update # type: ignore
from telegram.ext import Application, ApplicationHandlerStop, MessageHandler, filters , ContextTypes, CommandHandler,CallbackQueryHandler # type: ignore

from handlers import inventario
from handlers.rewards import manejar_imagenes
from handlers.welcoming import nuevo_usuario,mensaje_de_presentaciones
from handlers.general import dar,ver,regalar,numero_azar,quitar,get_receptor
from handlers.theme_juegosYcasino import apostar,aceptar,detectar_dado,cancelar_apuesta,jugar,robar
from handlers.starting_menu import start,menu_callback
from handlers.tienda import tienda,tienda_callback
from handlers.inventario import inventario,inventario_callback,usar
from config import BOT_TOKEN, DOMS, obtener_temas_por_comunidad

RUTA_CASTIGADOS = "castigados.json"

def cargar_castigados():
    if not os.path.exists(RUTA_CASTIGADOS):
        return {}
    try:
        with open(RUTA_CASTIGADOS, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Convertir listas a sets
            return {int(k): set(v) for k, v in data.items()}
    except:
        return {}
def guardar_castigados(data):
    # Convertir sets a listas para poder guardarlos
    serializable = {str(k): list(v) for k, v in data.items()}
    with open(RUTA_CASTIGADOS, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=4, ensure_ascii=False)

async def get_theme_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        thread_id = update.message.message_thread_id
        chat_id = update.effective_chat.id
        await update.message.reply_text(
            f"📌 Chat ID: `{chat_id}`\n"
            f"📌 Theme (message_thread_id): `{thread_id}`",
            parse_mode="Markdown"
        )
async def saludar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_bienvenida = (
        "🎄✨ *¡Ho, ho, ho! Llegó PiBot al chat* ✨🎄\n"
        "¡Hola a todos! 🤖🎅\n"
        "Estoy aquí para traer *alegría, buena vibra y espíritu navideño* a este lugar.\n"
        "Prepárense para luces, diversión y un montón de sorpresas festivas. 🎁❄️\n\n"
        "¡Que comience la magia navideña! 🎅🤖✨"
    )
    await update.message.reply_text(mensaje_bienvenida, parse_mode="Markdown")
async def castigar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    actor_id = update.effective_user.id

    if chat_id != -1003290179217:
        await update.message.reply_text("❌ Este comando no está habilitado en este grupo.")
        return
    
    if actor_id not in DOMS:
        await update.message.reply_text("❌ No tienes permisos para usar este comando.")
        return
    
    usuario_objetivo = await get_receptor(update, context, 1)
    if usuario_objetivo in (False, None):
        await update.message.reply_text("❌ No pude identificar al usuario objetivo.")
        return
    
    target_id = usuario_objetivo.id
    target_username = usuario_objetivo.username

    if target_id not in DOMS[actor_id]:
        try:
            await update.message.reply_text(f"❌ No puedes castigar a {target_username}. No tienes control sobre él/ella")
        except AttributeError:
            await context.bot.send_message(f"❌ No puedes castigar a {target_username}. No tienes control sobre él/ella")
        return

    # --- Cargar JSON
    castigados = cargar_castigados()

    if chat_id not in castigados:
        castigados[chat_id] = set()

    castigados[chat_id].add(target_id)

    # --- Guardar JSON
    guardar_castigados(castigados)

    await update.message.reply_text(
        f"🔇 @{target_username} te has portado mal. "
        "Ahora tendrás que quedarte en el rincón hasta que te perdonen."
    )
async def filtro_castigo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    user_id = update.effective_user.id

    rincon_id = obtener_temas_por_comunidad(-1003290179217)["theme_rincon"]

    # --- Cargar JSON
    castigados = cargar_castigados()

    if chat_id not in castigados:
        return
    
    if user_id not in castigados[chat_id]:
        return

    topic = update.message.message_thread_id

    if topic != rincon_id:
        try:
            await update.message.delete()
            await context.bot.send_message(
                chat_id=chat_id,
                message_thread_id=topic,
                text=f"Oh oh... @{username} fue atrapado fuera del rincón :)"
            )
        except:
            pass
    
async def perdonar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    actor_id = update.effective_user.id

    if chat_id != -1003290179217:
        await update.message.reply_text("❌ Este comando no está habilitado en este grupo.")
        return

    if actor_id not in DOMS:
        await update.message.reply_text("❌ No tienes permiso para usar este comando.")
        return

    usuario_objetivo = await get_receptor(update, context, args_length=1)

    if usuario_objetivo in (False, None):
        await update.message.reply_text("❌ No pude identificar al usuario que deseas perdonar.")
        return

    target_id = usuario_objetivo.id
    target_username = usuario_objetivo.username or "SinUsername"

    if target_id not in DOMS[actor_id]:
        await update.message.reply_text(f"❌ No puedes perdonar a @{target_username}.")
        return

    # --- Cargar JSON
    castigados = cargar_castigados()

    if chat_id not in castigados or target_id not in castigados[chat_id]:
        await update.message.reply_text(f"ℹ️ @{target_username} no está castigado.")
        return

    # --- Quitar castigo
    castigados[chat_id].remove(target_id)

    # Si queda vacío, eliminar el chat
    if not castigados[chat_id]:
        del castigados[chat_id]

    # --- Guardar JSON
    guardar_castigados(castigados)

    await update.message.reply_text(
        f"✅ @{target_username} ha sido perdonado. Ya puede hablar en todos los temas."
    )
async def bloquear_comunidad(update, context):
    # Algunos updates no tienen chat (ej: callbacks muy raros)
    if not update.effective_chat:
        return

    if update.effective_chat.id == -1003397946543:
        # Solo responder si es comando o mensaje normal
        if update.message:
            await update.message.reply_text(
                "este bot no esta habilitado para esta comunidad"
            )

        # 🔴 Detiene TODOS los handlers siguientes
        raise ApplicationHandlerStop()
def main():
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, bloquear_comunidad), group=-1)
    app.add_handler(CommandHandler("start", start),group = 0)
    app.add_handler(CommandHandler("castigar",castigar),group = 0)
    app.add_handler(CommandHandler("perdonar", perdonar),group = 0)
    
    # Handlers juegos
    app.add_handler(CommandHandler("apostar", apostar),group=1)
    app.add_handler(CommandHandler("aceptar", aceptar),group=1)
    app.add_handler(CommandHandler("cancelar", cancelar_apuesta),group=1)
    app.add_handler(CommandHandler("robar", robar),group=1)
    app.add_handler(CommandHandler("jugar", jugar),group=1)
    app.add_handler(CommandHandler("usar", usar), group=1)
    app.add_handler(MessageHandler(filters.Dice.DICE, detectar_dado),group=1)

    app.add_handler(CommandHandler("tienda", tienda),group=2)
    app.add_handler(CommandHandler("inventario", inventario),group=2)
    app.add_handler(CommandHandler("ver", ver),group=2)
    app.add_handler(CommandHandler("regalar", regalar),group=2)
    app.add_handler(CommandHandler("dar", dar),group=2)
    app.add_handler(CommandHandler("quitar", quitar),group=2)
    app.add_handler(CommandHandler("NumAzar", numero_azar),group=2)
    app.add_handler(CommandHandler("id", get_theme_id),group=2)
    app.add_handler(CommandHandler("saludar", saludar),group=2)

    # Handlers recompensas
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION, manejar_imagenes),group=3)

    # Handlers de bienvenida
    #app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, nuevo_usuario), group=4)
    #app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_de_presentaciones), group=4)

    # CallBacks
    app.add_handler(CallbackQueryHandler(menu_callback,pattern="^(ver_comandos|abrir_tienda|ver_inventario|perfil)$"),group=5)
    app.add_handler(CallbackQueryHandler(inventario_callback,pattern="^(inv_prev_|inv_next_|ver_item_)"),group=5)
    app.add_handler(CallbackQueryHandler(tienda_callback,pattern="^(producto_|volver_menu|abrir_tienda|volver_catalogo|comprar_)"),group=5)

    # Handler de filtro castigo
    app.add_handler(MessageHandler(filters.ALL,filtro_castigo),group=6)

    # Handler general (para todos los chats)
    
    print("🤖 Bot corriendo...")
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()