# handlers/imagen_presentaciones.py
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from config import obtener_temas_por_comunidad
from sqlgestion import normalizar_nombre,get_campo_usuario,insert_user,dar_puntos

contador_imagenes_multimedia = {}
contador_imagenes_nsfw = {}
contador_imagenes_presentacion = []

async def manejar_imagenes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message == None:
        return
    group_id = update.effective_chat.id
    CHAT_IDS = obtener_temas_por_comunidad(group_id)
    thread_id = update.message.message_thread_id

    if thread_id == CHAT_IDS["theme_multimedia"]:
        await detectar_imagenes_multimedia(update, context)
        return
    if group_id != -1003290179217: 
        if thread_id == CHAT_IDS["theme_presentaciones"]:
            await detectar_imagen_presentacion(update, context)
            return
    else:
        if thread_id == None:
            await detectar_imagen_presentacion(update, context)
            return
    if thread_id == CHAT_IDS["theme_NSFW"]:
        await detectar_imagenes_nsfw(update,context)
        return
    if thread_id == CHAT_IDS["theme_Exhibicionismo"]:
        await detectar_exhibicion(update,context)
        return
    
async def detectar_imagen_presentacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    # DEBUG: mostrar atributos del mensaje
    thread_id = getattr(msg, "message_thread_id", None)

    # 2) Detectar si el mensaje contiene imagen (photo) o archivo de imagen (document)
    tiene_photo = bool(msg.photo)
    tiene_document_image = False
    if msg.document and getattr(msg.document, "mime_type", ""):
        if msg.document.mime_type.startswith("image/"):
            tiene_document_image = True

    if not (tiene_photo or tiene_document_image):
        return

    # 4) Cargar usuarios con la función del general
    user = msg.from_user
    user_id = user.id
    username = user.username
    nombre = normalizar_nombre(user.first_name,user.last_name)

    # comprobar campo personalizado 'primera_imagen_presentacion'
    if user_id in contador_imagenes_presentacion:
        return

    if get_campo_usuario(user_id,"id_user") is None:
        insert_user(user_id,0,username,nombre)
    
    contador_imagenes_presentacion.append(user_id)
    dar_puntos(user_id,5)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📸 {username or nombre}, gracias por presentarte con imagen 😁 como recompensa, te hemos otorgado tus primeros 5 pipesos 🌟 \n Puedes ganar más participando activamente en la comunidad, recuerda leer las reglas y pasarla bien con el resto de gente 🥰",
        message_thread_id=thread_id
    )

async def detectar_imagenes_multimedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detecta imágenes en el tema multimedia y recompensa al usuario cada 3 enviadas."""
    mensaje = update.message

    if not mensaje:
        return

    tiene_foto = bool(mensaje.photo)
    tiene_video = bool(mensaje.video)
    tiene_gif = bool(mensaje.animation)

    if not (tiene_foto or tiene_video or tiene_gif):
        return

    thread_id = mensaje.message_thread_id
    user = mensaje.from_user

    user_id = user.id
    username = user.username
    nombre = normalizar_nombre(user.first_name,user.last_name)

    # Inicializar contador
    if user_id not in contador_imagenes_multimedia:
        contador_imagenes_multimedia[user_id] = 0

    # Incrementar contador de imágenes consecutivas
    contador_imagenes_multimedia[user_id] += 1

    # Recompensa cada 3 imágenes
    if contador_imagenes_multimedia[user_id] >= 3:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🎉 @{username or nombre} ha sido recompensado con 10 PiPesos por su actividad en multimedia 📸",
            message_thread_id=thread_id
        )
        if get_campo_usuario(user_id,"id_user") is None:
            insert_user(user_id,0,username,nombre)
        dar_puntos(user_id,10)

        # Reiniciar contador del usuario
        contador_imagenes_multimedia[user_id] = 0

    # Reinicio automático del contador después de 2 minutos sin enviar fotos
    async def resetear_contador(user_id):
        await asyncio.sleep(120)
        contador_imagenes_multimedia[user_id] = 0

    asyncio.create_task(resetear_contador(user_id))

async def detectar_imagenes_nsfw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detecta imágenes en el tema NSFW y recompensa con 10 PiPesos cada 5 imágenes seguidas."""
    mensaje = update.message

    if not mensaje:
        return

    tiene_foto = bool(mensaje.photo)
    tiene_video = bool(mensaje.video)
    tiene_gif = bool(mensaje.animation)

    if not(tiene_foto or tiene_video or tiene_gif):
        return
    
    thread_id = mensaje.message_thread_id
    user = mensaje.from_user

    # ✅ Solo se ejecuta en el tema NSFW

    user_id = user.id
    username = user.username
    nombre = normalizar_nombre(user.first_name,user.last_name)

    # Inicializar contador si no existe
    if user_id not in contador_imagenes_nsfw:
        contador_imagenes_nsfw[user_id] = 0

    # Incrementar contador de imágenes consecutivas
    contador_imagenes_nsfw[user_id] += 1

    # Recompensa cada 5 imágenes
    if contador_imagenes_nsfw[user_id] >= 5:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🔥 @{username or nombre} ha sido recompensado con 19 PiPesos por su actividad en NSFW 😏",
            message_thread_id=thread_id
        )
        if get_campo_usuario(user_id,"id_user") is None:
            insert_user(user_id,0,username,nombre)
        dar_puntos(user_id,16)

        # Reiniciar contador del usuario
        contador_imagenes_nsfw[user_id] = 0
    # Reinicio automático del contador después de 2 minutos sin enviar fotos
    async def resetear_contador(user_id):
        await asyncio.sleep(120)
        contador_imagenes_nsfw[user_id] = 0

    asyncio.create_task(resetear_contador(user_id))

async def detectar_exhibicion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Detecta imágenes, videos o GIFs en el canal Exhibición.
    Recompensa con 10 PiPesos por cada publicación multimedia.
    """
    mensaje = update.message
    if not mensaje:
        return

    # ✅ Detectar tipos de contenido multimedia
    tiene_foto = bool(mensaje.photo)
    tiene_video = bool(mensaje.video)
    tiene_gif = bool(mensaje.animation)  # Los GIFs llegan como "animation"

    if not (tiene_foto or tiene_video or tiene_gif):
        return  # Ignorar mensajes sin multimedia

    thread_id = mensaje.message_thread_id
    user = mensaje.from_user

    # ✅ Solo si el mensaje está en el canal de Exhibición

    user_id = user.id
    username = user.username
    nombre = normalizar_nombre(user.first_name,user.last_name)
    if get_campo_usuario(user_id,"id_user") is None:
        insert_user(user_id,0,username,nombre)
    
    # Cargar y actualizar usuarios
    dar_puntos(user_id,10)

    # ✅ Enviar mensaje de confirmación al mismo hilo
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✨ @{username or nombre} ha sido recompensado con 10 PiPesos por su publicación en Exhibicionismo 💫",
        message_thread_id=thread_id
    )