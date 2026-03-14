"""
GUÍA COMPLETA: Pruebas Locales de PiBot2.0

Este archivo proporciona instrucciones paso a paso para ejecutar
el bot localmente antes del deployment a producción.
"""

# ============================================================================
# PASO 0: REQUISITOS PREVIOS
# ============================================================================
"""
Antes de comenzar, asegúrate de tener:

1. Python 3.8+ instalado:
   - Windows: https://www.python.org/downloads/
   - Linux: sudo apt-get install python3
   - macOS: brew install python3

2. Git instalado (opcional pero recomendado):
   - https://git-scm.com/

3. Una cuenta de Telegram:
   - https://telegram.org/

4. Acceso a BotFather en Telegram:
   - Abre Telegram
   - Busca @BotFather
   - Escribe /start
   - Crea un nuevo bot
"""

# ============================================================================
# PASO 1: CONFIGURAR ENTORNO VIRTUAL
# ============================================================================
"""
Un entorno virtual aísla las dependencias de tu proyecto.

WINDOWS:
--------
# Crear el entorno virtual
python -m venv venv

# Activar el entorno
venv\\Scripts\\activate

LINUX / macOS:
--------------
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno
source venv/bin/activate

Deberías ver "(venv)" al inicio de tu terminal.
"""

# ============================================================================
# PASO 2: INSTALAR DEPENDENCIAS
# ============================================================================
"""
Con el entorno virtual activado, instala todas las dependencias:

pip install -r requirements.txt

Esto instalará:
  - aiogram (framework principal)
  - python-telegram-bot (API alternativa)
  - python-dotenv (manejo de .env)
  - APScheduler (tareas programadas)
  - pytest (testing)
  - black (formateador de código)
  - flake8 (linter)
  - Y muchas más...

Tiempo estimado: 2-5 minutos
"""

# ============================================================================
# PASO 3: OBTENER BOT TOKEN
# ============================================================================
"""
COMO OBTENER TU BOT TOKEN:

1. Abre Telegram
2. Busca y abre el chat con @BotFather
3. Escribe: /start
4. Escribe: /newbot
5. Elige un nombre para tu bot (ej: "MiPiBotTest")
6. Elige un username único (ej: "mipibottest_bot")
7. @BotFather te dará un token como este:
   1234567890:ABCDEFGHIJKLMNOpqrstuvwxyz-1a2b3c4d5e6f

COPIA ESE TOKEN - lo necesitarás en el siguiente paso
"""

# ============================================================================
# PASO 4: CREAR ARCHIVO .env
# ============================================================================
"""
El archivo .env contiene variables sensibles que NO deben ir a GitHub.

Ya debería existir .env en tu proyecto, pero si no, crear uno:

---CONTENIDO DE .env---
BOT_TOKEN=PEGA_TU_TOKEN_AQUI
DATABASE_FILE=usuarios.db
LOG_LEVEL=DEBUG
---FIN---

IMPORTANTE:
  ✅ El archivo .env está en .gitignore (no se sube a GitHub)
  ✅ Nunca compartas tu BOT_TOKEN públicamente
  ✅ Si lo haces, desactiva el bot desde @BotFather (/revoke)
"""

# ============================================================================
# PASO 5: VERIFICAR DEPENDENCIAS
# ============================================================================
"""
Ejecuta el script de verificación:

python verify_dependencies.py

Deberías ver:
  ✅ aiogram 3.22.0 (Framework principal)
  ✅ python-telegram-bot 22.5
  ✅ aiofiles 24.1.0 (Operaciones async en archivos)
  ✅ aiohttp 3.12.15 (Cliente HTTP async)
  ✅ pydantic 2.11.10 (Validación de datos)
  ✅ python-dotenv 1.0.0 (Variables de entorno)
  ✅ APScheduler 3.10.4 (Tareas programadas)
  ✅ requests 2.32.5 (Cliente HTTP sync)

  ✅ Instaladas: 8/8
  🎉 ¡Todas las dependencias están instaladas correctamente!
"""

# ============================================================================
# PASO 6: PROBAR IMPORTACIONES
# ============================================================================
"""
Ejecuta el script de prueba de importaciones:

python test_imports.py

Deberías ver:
  ✅ Importación: src.config
  ✅ Importación: src.database
  ✅ Importación: src.utils
  ✅ Importación: handlers.general

  ✅ 4/4 módulos importados correctamente
  🎉 ¡El proyecto está listo para pruebas locales!
"""

# ============================================================================
# PASO 7: EXECUTAR EL BOT LOCALMENTE
# ============================================================================
"""
Para ejecutar el bot en tu máquina:

python main.py

Deberías ver:
  🤖 PiBot iniciado e listo para recibir mensajes...

El bot ahora está escuchando mensajes en modo polling.
Presiona Ctrl+C para detenerlo.
"""

# ============================================================================
# PASO 8: PROBAR EL BOT EN TELEGRAM
# ============================================================================
"""
Ahora prueba tu bot:

1. En Telegram, busca tu bot por su @username
   (el que creaste en BotFather, ej: @mipibottest_bot)

2. Abre el chat con el bot

3. Envía: /start
   Deberías ver el menú principal

4. Prueba otros comandos:
   - /ver (ver saldo)
   - /tienda (abrir tienda)
   - /inventario (ver items)
   - /id (ver ID del chat)

5. En grupo, prueba comandos sociales:
   - /dar 10 @username (transferir moneda)
   - /jugar (juego de dados)
   - /apostar 50 (crear apuesta)

Si algo falla, verás los errores en la terminal donde corre el bot.
"""

# ============================================================================
# PASO 9: PROBAR EN GRUPO (OPCIONAL)
# ============================================================================
"""
Para probar funcionalidades de grupo:

1. Crea un grupo de prueba en Telegram
2. Busca tu bot y agrégalo al grupo
3. Usa /id en el grupo para obtener:
   - Chat ID
   - Topic ID

4. Actualiza src/config/settings.py con estos IDs

5. Prueba comandos de grupo:
   - /jugar
   - /apostar
   - /robar

IMPORTANTE: Necesitas hacer que tu grupo tenga temas (topics) habilitados
"""

# ============================================================================
# PASO 10: DEBUGGING Y LOGS
# ============================================================================
"""
Si algo no funciona:

1. Revisa la terminal donde corre el bot (busca errores)

2. Aumenta el nivel de logging en .env:
   LOG_LEVEL=DEBUG

3. Verifica el token en .env (¡sin comillas!)

4. ¿El bot no responde?
   - ¿Está el bot agregado al grupo?
   - ¿Tiene permisos de lectura/escritura?
   - ¿Está corriendo el script main.py?

5. ¿Errores de base de datos?
   - Borra usuarios.db y deja que se cree de nuevo
   - Asegúrate de que usuarios.db existe en la carpeta correcta

6. Errores de importación?
   - Ejecuta: python test_imports.py
   - Instala dependencias faltantes con pip
"""

# ============================================================================
# PASO 11: PRUEBAS AUTOMATIZADAS (OPCIONAL)
# ============================================================================
"""
Para ejecutar tests (si tienes alguno):

python -m pytest tests/

Esto ejecutará todos los tests en la carpeta tests/
"""

# ============================================================================
# PASO 12: LIMPIAR LA TERMINAL (OPCIONAL)
# ============================================================================
"""
Para ver solo los logs del bot más claramente:

# En una terminal nueva, mantén el bot corriendo en otra
# Luego ejecuta en esta nueva terminal:

python -u main.py 2>&1 | tee bot.log

Esto guardará todos los logs en bot.log y los mostrará en pantalla
"""

# ============================================================================
# CHECKLIST PRE-DEPLOYMENT
# ============================================================================
"""
Antes de hacer deploy a Replit/Heroku/etc:

✅ Bot corre localmente sin errores
✅ /start funciona en chat privado
✅ Comandos básicos funcionan (/ver, /dar, etc)
✅ Bot responde en grupos
✅ Base de datos guarda datos correctamente
✅ No hay secretos en el código
✅ .env contiene BOT_TOKEN válido
✅ requirements.txt está actualizado
✅ Código está formateado (black src/)
✅ Linting pasa (flake8 src/)
✅ README.md está actualizado
✅ Documentación está completa
"""

# ============================================================================
# ESTRUCTURA DEL PROYECTO PARA REFERENCIA
# ============================================================================
"""
PiBot2.0/
├── .env                    # Variables de entorno (NO commitear)
├── .env.example            # Plantilla de .env
├── .gitignore              # Archivos ignorados por git
├── .venv/                  # Entorno virtual
├── main.py                 # Punto de entrada del bot
├── requirements.txt        # Dependencias
│
├── src/                    # Código principal
│   ├── config/            # Configuración
│   │   ├── settings.py    # Configuración principal
│   │   └── __init__.py
│   ├── database/          # Operaciones de base de datos
│   │   ├── database.py    # Módulo de BD
│   │   └── __init__.py
│   ├── handlers/          # Manejadores de comandos
│   │   └── *.py          # Diferentes handlers
│   ├── utils/             # Utilidades
│   │   ├── helpers.py
│   │   └── __init__.py
│   └── __init__.py
│
├── handlers/              # Handlers legacy (todavía usados)
├── gifs_items/            # GIFs para items
├── img_items/             # Imágenes para items
├── docs/                  # Documentación
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── DEPLOYMENT.md
│   └── CONFIGURATION.md
└── tests/                 # Tests (para el futuro)
"""

# ============================================================================
# COMANDOS RÁPIDOS DE REFERENCIA
# ============================================================================
"""
# Activar entorno virtual
Windows: venv\\Scripts\\activate
Linux/Mac: source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar dependencias
python verify_dependencies.py

# Probar importaciones
python test_imports.py

# Ejecutar bot
python main.py

# Formatear código
black src/

# Linting
flake8 src/

# Correr tests
python -m pytest tests/

# Desactivar entorno virtual
deactivate
"""

# ============================================================================
# PROBLEMAS COMUNES
# ============================================================================
"""
P: "ModuleNotFoundError: No module named 'telegram'"
R: Falta instalar dependencias. Ejecuta: pip install -r requirements.txt

P: "ERROR: BOT_TOKEN environment variable is not set"
R: No existe .env o BOT_TOKEN no está definido. Crea el archivo .env

P: "Bot no responde a mensajes"
R: 
  - ¿Está el bot agregado al grupo/privado?
  - ¿El .env tiene un token válido?
  - ¿Está corriendo main.py?
  - Verifica en @BotFather que el bot esté activo

P: "Error de base de datos"
R: Borra usuarios.db y deja que se cree de nuevo automáticamente

P: "Errores de importación en handlers"
R: Los handlers viejos todavía existen. Se migrarán a src/handlers/ gradualmente
"""

# ============================================================================
# AYUDA ADICIONAL
# ============================================================================
"""
Para más información, lee:
  - README.md (guía general)
  - docs/ARCHITECTURE.md (estructura del código)
  - docs/DEVELOPMENT.md (desarrollo)
  - docs/DEPLOYMENT.md (deployment)
  - docs/CONFIGURATION.md (configuración detallada)

¡Buena suerte! 🚀
"""
