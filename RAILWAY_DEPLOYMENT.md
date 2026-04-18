# Deployment en Railway — Guía Completa

Railway es una plataforma moderna para hostear bots y aplicaciones. Toma ~5 minutos.

---

## Requisitos

- Cuenta en [Railway](https://railway.app)
- Repositorio en GitHub: `aleisnthere31/Pibotv2`
- Bot Token de Telegram (de @BotFather)

---

## PASO 1: Crear Cuenta en Railway

1. Ve a https://railway.app
2. Haz clic en **"Start Project"**
3. Elige **"Sign up with GitHub"**
4. Autoriza Railway para acceder a tu GitHub

---

## PASO 2: Crear Proyecto desde GitHub

1. En el dashboard, haz clic en **"New Project"**
2. Elige **"Deploy from GitHub repo"**
3. Selecciona: **`aleisnthere31/Pibotv2`**
4. Haz clic en **"Deploy"**

Railway clonará automáticamente tu repo.

---

## PASO 3: Añadir PostgreSQL

**Este paso es CRÍTICO** — el bot necesita PostgreSQL para funcionar.

1. En tu proyecto, haz clic en **"+ New"**
2. Selecciona **"Database"** → **"Add PostgreSQL"**
3. Railway creará una instancia de PostgreSQL y añadirá `DATABASE_URL` automáticamente

---

## PASO 4: Configurar Variables de Entorno

1. Abre tu servicio (el que tiene tu código)
2. Ve a la pestaña **"Variables"**
3. Agrega estas variables:

### Requeridas:

| Variable | Valor | Descripción |
|---|---|---|
| `BOT_TOKEN` | `tu_token_de_botfather` | Token del bot de Telegram |
| `BOT_USERNAME` | `PiBot` (sin @) | Username del bot para deep links |
| `BOTMASTER_IDS` | `123456789,987654321` | IDs de usuarios BotMaster (separados por coma) |

> **NOTA:** `DATABASE_URL` se configura automáticamente al añadir PostgreSQL en el Paso 3.

---

## PASO 5: Configurar el Comando de Inicio

Railway debería detectar el `Procfile` automáticamente. Si no:

1. Ve a **"Settings"** de tu servicio
2. Busca **"Start Command"**
3. Ingresa: `python main.py`

El `Procfile` del repo ya contiene:
```
worker: python main.py
```

---

## PASO 6: Desplegar

Railway despliega automáticamente cuando:
- Cambias variables de entorno
- Haces push a GitHub (rama `main`)

En los **Logs** deberías ver:
```
[INIT] Creating database if it doesn't exist...
[INIT] Creating tables...
[INIT] Seeding items catalog...
[INIT] Initializing BotMaster roles...
[INIT] Restarting active combats...
🤖 PiBot iniciado e listo para recibir mensajes...
```

---

## PASO 7: Verificar

1. Abre Telegram y busca tu bot por su @username
2. Envía `/start` — deberías ver el menú principal
3. Envía `/ver` — debería registrarte y mostrar tu saldo

---

## Troubleshooting

| Problema | Solución |
|---|---|
| Bot no responde | Revisa los logs en Railway. Verifica que `BOT_TOKEN` es correcto. |
| Error `DATABASE_URL not set` | Asegúrate de haber añadido PostgreSQL (Paso 3). |
| Tienda no abre | Verifica que `BOT_USERNAME` está configurado correctamente. |
| Error de permisos al asignar roles | Verifica que tu ID está en `BOTMASTER_IDS`. |
| Datos perdidos tras redeploy | No debería pasar — PostgreSQL persiste entre deploys. Si usas SQLite, migra a PostgreSQL. |
