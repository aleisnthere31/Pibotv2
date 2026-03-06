# starting_menu.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlgestion import get_campo_usuario
from handlers.tienda import tienda
from handlers.inventario import inventario

# =========  COMANDO /START  ========= #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if get_campo_usuario(user.id,"id_user") is None:
        await context.bot.send_message(
            chat_id=user.id,
            text=(
                "🎉 Veo que eres nuevo, no te tengo en mi sistema.\n\n"
                "Si deseas ingresar a la tienda o ver tu perfil,\n"
                "primero usa el comando /ver en la comunidad. 😄"
            )
        )
        return

    # Solo mostrar menú si está en privado
    if update.message.chat.type != "private":
        await update.message.reply_text("Envíame /start por privado para ver el menú.")
        return

    keyboard = [
        [InlineKeyboardButton("📜 Ver comandos", callback_data="ver_comandos")],
        [InlineKeyboardButton("🛍️ Abrir tienda", callback_data="abrir_tienda")],
        [InlineKeyboardButton("📦 Ver inventario", callback_data="ver_inventario")],
        [InlineKeyboardButton("👤 Perfil", callback_data="perfil")]
    ]

    await update.message.reply_text(
        "✨ **Menú principal**\nSelecciona una opción:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========  CALLBACK DEL MENÚ  ========= #
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    if data == "ver_comandos":
        await query.edit_message_text(
            "📜 *Comandos disponibles:*\n"
            "/tienda \n"
            "/perfil\n"
            "/ver\n"
            "/dar\n"
            "/jugar\n"
            "/robar\n"
            "/apostar\n"
            "/aceptar\n",
            parse_mode="Markdown"
        )

    elif data == "abrir_tienda":
        await tienda(update, context,from_menu=True)
        return

    elif data == "ver_inventario":
        await inventario(update,context)
        return

    elif data == "perfil":
        await query.edit_message_text(
            f"👤 *Perfil de {user.first_name}*\n"
            f"ID: `{user.id}`",
            parse_mode="Markdown"
        )
        return
