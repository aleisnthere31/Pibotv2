# 🚀 Deployment en Railway - Guía Completa

Railway es una plataforma moderna y fácil de usar para hostear bots y aplicaciones. Toma ~5 minutos.

---

## 📋 Requisitos

✅ Cuenta en Railway (https://railway.app)  
✅ Repositorio en GitHub (https://github.com/aleisnthere31/Pibotv2)  
✅ Bot Token de Telegram (de @BotFather)  

Eso es todo. **No necesitas tarjeta de crédito** para empezar (tienen créditos gratis).

---

## 🔑 PASO 1: Crear Cuenta en Railway

1. **Ve a https://railway.app**
2. Haz clic en **"Start Project"**
3. Elige **"Sign up with GitHub"** (más fácil)
4. Autoriza Railway para acceder a tu GitHub
5. ¡Listo! Ya estás registrado

---

## ⚙️ PASO 2: Crear Nuevo Proyecto

1. **En el dashboard de Railway**, haz clic en **"New Project"**
2. Elige **"Deploy from GitHub repo"**
3. **Si no autorizó GitHub aún**, haz clic en "Configure GitHub App"
4. Selecciona tu repositorio: **`aleisnthere31/Pibotv2`**
5. Haz clic en **"Deploy"**

Railway clonará automáticamente tu repo.

---

## 📦 PASO 3: Añadir Plugin de Python

Railway detectará automáticamente que es un proyecto Python. Si no:

1. En tu proyecto, haz clic en **"Add Service"** o **"+ New"**
2. Busca **"Python"**
3. Selecciona **"Python"** (latest)

---

## 🔐 PASO 4: Configurar Variables de Entorno

Este es el paso más importante. En Railway:

1. **Abre tu servicio Python**
2. Ve a la pestaña **"Variables"**
3. Haz clic en **"Add Variable"**
4. Agrega estas variables una por una:

### **BOT Configuration** (CRÍTICO):
```
BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOpqrstuvwxyz-1a2b3c4d5e6f
```
*(Reemplaza con tu token real de @BotFather)*

```
DATABASE_FILE=usuarios.db
```

```
LOG_LEVEL=INFO
```

### Variables Opcionales:
```
PYTHON_VERSION=3.11
```

---

## 🎯 PASO 5: Configurar el Comando de Inicio

Railway debería detectar automáticamente que tienes `requirements.txt` y ejecutar `main.py`.

Si no, configura manualmente:

1. **En tu servicio Python**
2. Ve a la pestaña **"Settings"** (engranaje)
3. Busca **"Start Command"** o **"Run Command"**
4. Ingresa:
```bash
pip install -r requirements.txt && python main.py
```

Si eso no funciona, prueba:
```bash
python main.py
```

---

## 🚀 PASO 6: Desplegar

Railway despliega automáticamente cuando:
- ✅ Cambias las variables
- ✅ Haces push a GitHub (en rama `main`)

**Para hacer deploy ahora:**

1. Haz clic en **"Deploy"** o espera a que Railway lo haga automáticamente
2. En la sección de **"Logs"**, verás el progreso
3. Espera a ver:
```
🤖 PiBot iniciado e listo para recibir mensajes...
```

---

## 📊 PASO 7: Verificar que Funciona

1. **Ve a Telegram**
2. **Busca tu bot por su @username**
3. **Envía `/start`**
4. **Deberías recibir respuesta**

Si sale error, revisa los **Logs** en Railway:
- Click en tu servicio
- Pestaña **"Logs"**
- Busca errores en rojo

---

## 🔄 Actualizaciones Automáticas

Railway es genial porque redeploy automáticamente cuando haces push a GitHub:

```bash
# En tu máquina local
git add .
git commit -m "tu cambio"
git push origin main
```

Railway verá el cambio en GitHub y redeploy automáticamente. **Sin hacer nada más.**

---

## 🛠️ Troubleshooting en Railway

### ❌ Error: "ModuleNotFoundError"

**Causa**: Las dependencias no se instalaron.

**Solución**:
1. Verifica que existe `requirements.txt` en la raíz
2. En Railway, abre **Settings** → busca "Install command"
3. Debería ser: `pip install -r requirements.txt`

---

### ❌ Error: "BOT_TOKEN environment variable is not set"

**Causa**: Falta la variable de entorno.

**Solución**:
1. Ve a **Variables**
2. Agrega: `BOT_TOKEN=tu_token_real`
3. Click **"Save"** o **"Apply"**
4. Railway redeploy automáticamente

---

### ❌ El bot se apaga después de unos minutos

**Causa**: Posible timeout o crash.

**Solución**:
1. Revisa los logs en Railway
2. Busca dónde dice "Error" o "Exception"
3. Comparte el error para debuggear

---

### ❌ "Spawn failed" o "Process exited"

**Causa**: El comando de inicio es incorrecto.

**Solución**:
1. Ve a **Settings** → **Start Command**
2. Prueba con: `python main.py`
3. Guarda y redeploy

---

## 📈 Monitoreo en Railway

Railway te muestra:

- **Status**: Verde = corriendo, Rojo = crash
- **CPU/Memory**: Uso de recursos
- **Logs**: Todos los outputs del bot
- **Deployments**: Historial de deploys

---

## 🔒 Seguridad

⚠️ **IMPORTANTE:**

- ✅ Nunca hagas commit de `.env` (ya está en `.gitignore`)
- ✅ Las variables en Railway son privadas
- ✅ Si expones BOT_TOKEN, ve a @BotFather → `/revoke` para desactivarlo
- ✅ Luego crea uno nuevo en @BotFather

---

## ⚡ Ventajas de Railway vs Otros

| Aspecto | Railway | fps.ms | Replit | Heroku |
|--------|---------|--------|--------|--------|
| Setup | ⚡ 2 min | 5 min | 3 min | 5 min |
| GitHub Integration | ✅ Automático | ❌ Manual | ⚠️ Limitado | ✅ Bueno |
| Auto Deploy | ✅ Sí | ❌ No | ⚠️ Limitado | ✅ Sí |
| Free Tier | ✅ $5/mes | ✅ Gratis* | ✅ Limitado | ❌ No |
| Dashboard | ✅ Excelente | ✅ Bueno | ✅ Simple | ✅ Bueno |
| 24/7 Uptime | ✅ Sí | ✅ Sí | ⚠️ Si está abierto | ✅ Sí |

---

## 💳 Planes en Railway

### Free Tier
- **$5 USD/mes en créditos gratis**
- Un bot simple usa ~$1-2/mes
- **Suficiente para empezar**

### Pro
- **$7 USD/mes** (después de gastar los gratis)
- Más recursos
- Soporte prioritario

---

## 📞 Comandos Útiles (Railway CLI)

Si instalas Railway CLI (opcional):

```bash
# Instalar
npm install -g @railway/cli

# Login
railway login

# Ver logs
railway logs

# Ver variables
railway variables

# Actualizar variable
railway variables set BOT_TOKEN=nuevo_token
```

---

## ✅ Checklist Final

- [ ] Cuenta en Railway creada
- [ ] Proyecto creado (conectado a GitHub)
- [ ] Python service añadido
- [ ] BOT_TOKEN configurado
- [ ] DATABASE_FILE configurado
- [ ] Start Command correcto
- [ ] Proyecto deplorado (Status verde)
- [ ] Bot responde a `/start` en Telegram
- [ ] Logs no muestran errores

---

## 🎉 ¡Listo!

Si todo funciona, tu bot está corriendo en Railway 24/7 🚀

**Próximos pasos**:
1. Invita a colaboradores a tu GitHub
2. Haz push de cambios y mira cómo Railway redeploy automáticamente
3. Monitorea los logs regularmente
4. Escala a plan Pro cuando sea necesario

---

## 📚 Enlaces Útiles

- Railway: https://railway.app
- Tu Proyecto: https://railway.app/dashboard
- Documentación: https://docs.railway.app
- Discord Comunidad: https://discord.gg/railway

¡Que disfrutes tu bot en Railway! 🤖
