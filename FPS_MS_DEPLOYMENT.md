# 🚀 Deployment en fps.ms - Guía Completa

fps.ms es una plataforma de hosting basada en Docker. Esta guía te ayudará a deployer PiBot2.0 en fps.ms de forma rápida y segura.

---

## 📋 Requisitos Previos

✅ Cuenta en fps.ms (https://fps.ms)  
✅ Repositorio en GitHub (https://github.com/aleisnthere31/Pibotv2)  
✅ Bot Token de Telegram (de @BotFather)  
✅ Personal Access Token de GitHub  

---

## 🔑 PASO 1: Crear Personal Access Token en GitHub

Este token permitirá que fps.ms clonar tu repositorio de forma segura.

### Instrucciones:

1. **Ve a GitHub**:
   - Abre https://github.com/settings/tokens
   - O: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Crea un nuevo token**:
   - Haz clic en **"Generate new token"** → **"Generate new token (classic)"**
   - Dale un nombre: `fps.ms PiBot Deployment`

3. **Selecciona estos permisos**:
   ```
   ✅ repo (acceso completo a repositorios)
   ✅ workflow (para GitHub Actions, si lo usas)
   ```

4. **Copia el token**:
   - Haz clic en **"Generate token"**
   - **COPIA INMEDIATAMENTE** el token que aparece (⚠️ No podrás verlo de nuevo)
   - Guárdalo en un lugar seguro (lo necesitarás en fps.ms)

### Token de ejemplo:
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🤖 PASO 2: Obtener Bot Token de Telegram

(Si ya lo tienes, salta a PASO 3)

1. Abre Telegram
2. Busca **@BotFather**
3. Envía `/newbot`
4. Sigue las instrucciones para crear un bot
5. Copia el token que te da:
   ```
   1234567890:ABCDEFGHIJKLMNOpqrstuvwxyz-1a2b3c4d5e6f
   ```

---

## 🎮 PASO 3: Configurar fps.ms

### 3.1 Crear Nuevo Servidor

1. **Inicia sesión en fps.ms**
   - Ve a https://fps.ms
   - Inicia sesión con tu cuenta

2. **Crea un servidor nuevo**
   - Busca la opción "Create Server" o "New Server"
   - Elige cualquier nombre: `PiBot` o `PiBot2.0`

### 3.2 Configurar Docker Image

En la página de configuración, deberías ver un campo "Docker Image":

```
Python 3.11
```

✅ **Esta opción ya está disponible** - Úsala

---

## ⚙️ PASO 4: Configurar Startup Command

Reemplaza el Startup Command con este (adaptado para PiBot):

```bash
if [[ -d .git ]] && [[ "1" == "1" ]] && [ -n "${USERNAME}" ] && [ -n "${ACCESS_TOKEN}" ]; then git remote set-url origin "https://${USERNAME}:${ACCESS_TOKEN}@$(echo -e ${GIT_ADDRESS} | cut -d/ -f3-)"; if [ -n "${BRANCH}" ]; then git pull origin "${BRANCH}"; else git pull; fi; fi; if [ -n "" ]; then pip install -U --prefix .local ; fi; if [ -f "/home/container/${REQUIREMENTS_FILE}" ]; then pip install -U --prefix .local -r "${REQUIREMENTS_FILE}"; fi; /usr/local/bin/python "/home/container/main.py"
```

**¿Qué hace este comando?**
1. Configura Git con tus credenciales de GitHub
2. Descarga el código más reciente
3. Instala las dependencias de requirements.txt
4. Ejecuta main.py

---

## 🔐 PASO 5: Configurar Variables de Entorno

En fps.ms, busca una sección de "Environment Variables" o "Config" y agrega estas variables:

### Variables Requeridas (Git):
```
USERNAME=aleisnthere31
ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GIT_ADDRESS=github.com/aleisnthere31/Pibotv2
BRANCH=main
REQUIREMENTS_FILE=requirements.txt
```

### Variables del Bot (IMPORTANTES):
```
BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOpqrstuvwxyz-1a2b3c4d5e6f
DATABASE_FILE=usuarios.db
LOG_LEVEL=INFO
```

### Explicación de cada variable:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `USERNAME` | `aleisnthere31` | Tu usuario de GitHub |
| `ACCESS_TOKEN` | `ghp_xxx...` | Token personal de GitHub (creado en PASO 2) |
| `GIT_ADDRESS` | `github.com/aleisnthere31/Pibotv2` | URL del repositorio (sin https://) |
| `BRANCH` | `main` | Rama a descargar (main es la principal) |
| `REQUIREMENTS_FILE` | `requirements.txt` | Archivo de dependencias |
| `BOT_TOKEN` | `1234567890:ABCxxx...` | Token de tu bot de Telegram |
| `DATABASE_FILE` | `usuarios.db` | Nombre del archivo de BD |
| `LOG_LEVEL` | `INFO` | Nivel de logs (DEBUG, INFO, WARNING, ERROR) |

---

## 🚀 PASO 6: Iniciar Servidor

1. **Guarda la configuración**
   - Busca un botón "Save" o "Apply"

2. **Inicia el servidor**
   - Busca un botón "Start" o "Run"
   - El servidor debería iniciar en 30-60 segundos

3. **Verifica los logs**
   - Deberías ver algo como:
   ```
   🤖 PiBot iniciado e listo para recibir mensajes...
   ```

---

## 📊 PASO 7: Verificar que Funciona

1. **Ve a Telegram**
   - Busca tu bot por su @username
   - Envía `/start`
   - Deberías recibir respuesta

2. **Prueba comandos**
   - `/ver` - Ver saldo
   - `/tienda` - Ver tienda
   - `/inventario` - Ver items

3. **Revisa los logs en fps.ms**
   - Si hay errores, aparecerán en los logs
   - Busca errores como "BOT_TOKEN" no encontrado

---

## 🔧 Troubleshooting

### ❌ Error: "BOT_TOKEN environment variable is not set"
**Solución**: Verifica que BOT_TOKEN esté en las variables de entorno de fps.ms

### ❌ Error: "Repository not found"
**Solución**: Verifica que:
- ✅ USERNAME = tu usuario GitHub (ej: `aleisnthere31`)
- ✅ ACCESS_TOKEN = token válido y con permisos `repo`
- ✅ GIT_ADDRESS = sin `https://` (ej: `github.com/aleisnthere31/Pibotv2`)

### ❌ Error: "ModuleNotFoundError"
**Solución**: El archivo requirements.txt no se instaló correctamente
- Verifica que `REQUIREMENTS_FILE=requirements.txt`
- En fps.ms, busca los logs de instalación

### ❌ El bot se apaga después de unos minutos
**Solución**: Verifica que el Startup Command es correcto y no hay errores en los logs

### ❌ Error "Master branch not found"
**Solución**: Cambia el BRANCH a `main` (no `master`)

---

## 📈 Optimizaciones Opcionales

### 1. Aumentar Memoria RAM
Si el bot tiene problemas de rendimiento:
- En fps.ms, busca opciones de "RAM" o "Memory"
- Aumenta a 512MB o 1GB si es posible

### 2. Usar Puerto Personalizado
Si fps.ms lo permite, configura un puerto específico en variables:
```
PORT=8080
```

### 3. Logs Detallados
Para debugging, cambia LOG_LEVEL a DEBUG:
```
LOG_LEVEL=DEBUG
```

---

## 🔄 Actualizar Código en fps.ms

Después de hacer cambios en GitHub:

1. **Haz commit y push en tu máquina**:
```bash
git add .
git commit -m "tu mensaje"
git push origin main
```

2. **En fps.ms**:
   - Reinicia el servidor (botón "Restart")
   - El servidor descargará automáticamente el código nuevo

---

## 📊 Monitoreo Continuo

En fps.ms, deberías poder ver:

✅ **Status**: Server está corriendo (verde)  
✅ **CPU Usage**: Generalmente <5%  
✅ **RAM Usage**: Generalmente <50MB  
✅ **Logs**: Mensajes de estado del bot  

Si alguno de estos indica problemas, revisa los logs para encontrar el error.

---

## 🔒 Seguridad - IMPORTANTE

⚠️ **Nunca hagas esto**:
- ❌ No compartas tu ACCESS_TOKEN públicamente
- ❌ No subas .env a GitHub
- ❌ No muestres tu BOT_TOKEN en chats públicos

✅ **Si algo se expone**:
- Ve a GitHub → Settings → Developer settings → Tokens
- Haz clic en "Delete" ese token
- Crea uno nuevo
- Actualiza la variable en fps.ms

---

## ✅ Checklist Final

Antes de finalizar:

- [ ] Username de GitHub es correcto
- [ ] Access Token de GitHub funciona
- [ ] GIT_ADDRESS es correcto (sin https://)
- [ ] BRANCH = main
- [ ] BOT_TOKEN es válido (de @BotFather)
- [ ] DATABASE_FILE = usuarios.db
- [ ] REQUIREMENTS_FILE = requirements.txt
- [ ] Docker Image = Python 3.11
- [ ] Startup Command está copiado correctamente
- [ ] Servidor inicia sin errores
- [ ] Bot responde a /start en Telegram

---

## 📞 Si Tienes Problemas

1. **Revisa los logs en fps.ms** - el error está ahí
2. **Verifica cada variable de entorno** - asegúrate de que NO hay espacios extra
3. **Prueba localmente primero** - `python main.py` funciona en tu máquina?
4. **Actualiza GitHub** - asegúrate de que todo está pusheado

---

## 🎉 ¡Listo!

Si llegaste aquí, tu bot está corriendo en fps.ms 🚀

**Próximos pasos**:
- Invita a colaboradores a tu GitHub
- Configura más comandos en los handlers
- Agrega tests automáticos si lo deseas
- Monitorea los logs regularmente

¡Que disfrutes tu bot! 🤖
