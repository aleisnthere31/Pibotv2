"""
Role management handler for PiBot.

Internal role system:
  1 = Usuario (User)
  2 = Admin
  3 = BotMaster

Commands:
  /AsignarRol @usuario [1|2|3]  — Only BotMaster can use this
"""

from telegram import Update
from telegram.ext import ContextTypes
from src.database.database import get_id_user, get_user_role, set_user_role, check_permission, set_suerte

ROLE_NAMES = {1: "Usuario", 2: "Admin", 3: "BotMaster"}


async def asignar_rol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command: /AsignarRol @usuario [1|2|3]
    Only BotMaster (role=3) can assign roles.
    """
    sender = update.effective_user

    # Permission check: BotMaster only
    if not check_permission(sender.id, 3):
        await update.message.reply_text(
            "❌ Solo el BotMaster puede asignar roles."
        )
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "📋 Uso: /AsignarRol @usuario [1|2|3]\n\n"
            "Roles:\n"
            "  1 = Usuario\n"
            "  2 = Admin\n"
            "  3 = BotMaster"
        )
        return

    # Parse target user
    mention = context.args[0].lstrip("@")
    if not mention:
        await update.message.reply_text("⚠️ Debes mencionar un usuario con @.")
        return

    target_id = get_id_user(mention)
    if target_id is None:
        await update.message.reply_text(
            f"❌ No encontré a @{mention} en el sistema.\n"
            "El usuario debe haberse registrado primero con /ver."
        )
        return

    # Parse role
    try:
        role = int(context.args[1])
        if role not in (1, 2, 3):
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ El rol debe ser 1, 2 o 3.")
        return

    # Set role
    if set_user_role(target_id, role):
        role_name = ROLE_NAMES.get(role, "Desconocido")
        await update.message.reply_text(
            f"✅ @{mention} ahora tiene el rol: **{role_name}** ({role})",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text("❌ Error al asignar el rol.")


async def ver_rol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command: /MiRol
    Show the user's current internal role.
    """
    user = update.effective_user
    role = get_user_role(user.id)

    if role == 0:
        await update.message.reply_text(
            "⚠️ No estás registrado en el sistema. Usa /ver para registrarte."
        )
        return

    role_name = ROLE_NAMES.get(role, "Desconocido")
    await update.message.reply_text(
        f"👤 Tu rol actual: **{role_name}** ({role})",
        parse_mode="Markdown",
    )


SUERTE_PROB = {1: "0/3", 2: "1/3", 3: "2/3"}


async def suerte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command: /Suerte @usuario [1|2|3]
    Only BotMaster (role=3) can set a user's luck value.
    """
    sender = update.effective_user

    if not check_permission(sender.id, 3):
        await update.message.reply_text("❌ Solo el BotMaster puede usar este comando.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "📋 Uso: /Suerte @usuario [1|2|3]\n\n"
            "Valores:\n"
            "  1 = Sin suerte (0/3)\n"
            "  2 = Normal (1/3)\n"
            "  3 = Mucha suerte (2/3)"
        )
        return

    mention = context.args[0].lstrip("@")
    if not mention:
        await update.message.reply_text("⚠️ Debes mencionar un usuario con @.")
        return

    target_id = get_id_user(mention)
    if target_id is None:
        await update.message.reply_text(
            f"❌ No encontré a @{mention} en el sistema.\n"
            "El usuario debe haberse registrado primero con /ver."
        )
        return

    try:
        valor = int(context.args[1])
        if valor not in (1, 2, 3):
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ El valor de suerte debe ser 1, 2 o 3.")
        return

    if set_suerte(target_id, valor):
        prob = SUERTE_PROB.get(valor, "?")
        await update.message.reply_text(
            f"🍀 Se ha actualizado la suerte de @{mention} a {valor} "
            f"(Probabilidad de robo: {prob})"
        )
    else:
        await update.message.reply_text("❌ Error al actualizar la suerte.")
