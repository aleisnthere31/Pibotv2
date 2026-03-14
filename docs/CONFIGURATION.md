# Configuration Reference

This document provides a detailed reference for all configuration options and setup procedures.

## Environment Variables

### Required Variables

```
BOT_TOKEN=your_telegram_bot_token_here
```

- **Source**: Get from [@BotFather](https://t.me/botfather) on Telegram
- **Required**: Yes
- **Type**: String
- **Example**: `BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh`

### Optional Variables

```
DATABASE_FILE=usuarios.db
```

- **Description**: Path to SQLite database file
- **Default**: `usuarios.db` (in project root)
- **Type**: String
- **Example**: `DATABASE_FILE=/var/lib/pibot/usuarios.db`

```
LOG_LEVEL=INFO
```

- **Description**: Logging verbosity level
- **Default**: `INFO`
- **Type**: String
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Example**: `LOG_LEVEL=DEBUG`

## Community Configuration

Edit `src/config/settings.py` to add or modify communities:

### Adding a New Community

```python
COMUNIDADES = [
    {
        "id_comunidad": -1003290179217,  # Chat ID (get with /id command)
        "nombre": "Community Name",
        "temas": {
            "theme_anuncios": 526,        # Announcements
            "theme_juegosYcasino": 528,   # Games/Casino
            "theme_multimedia": 688,      # Media posts
            "theme_NSFW": 2,              # Adult content
            "theme_rincon": 77167,        # Punishment corner
            # Add more topics as needed
        }
    }
]
```

**How to get Chat ID and Topic IDs**:
1. In the group, send: `/id`
2. Bot responds with:
   ```
   Chat ID: -1003290179217
   Topic: 528
   ```
3. Add these to your configuration

### Admin Configuration

Set admin users per community in `src/config/settings.py`:

```python
ADMINS = [
    {
        "id_comunidad": -1003290179217,  # Community
        "admins": {
            1128700552,
            7745029153,
            5708369612,
        }
    }
]
```

**How to get User IDs**:
1. Send `/start` in bot's private chat
2. Forward a message from the user to the bot
3. Bot will show their ID in logs
4. Or manually forward and check

### DOM (Dominant) Configuration

Configure DOM users and their submissives:

```python
DOMS = {
    1370162159: [5661536115],           # DOM: [submissive, submissive, ...]
    1174798556: [7064982957, 7819911906],
}
```

Only DOM users can use `/castigar` and `/perdonar` commands on their submissives.

## Item Configuration

### Adding Items to Shop

```python
from src.database import insert_item

# Add item to catalog
insert_item(
    nombre="Collar",           # Item name
    precio=50,                 # Price in PiPesos
    ruta_imagen="img_items/collar.png",  # Image path
    descripcion="A leather collar",      # Description shown in shop
    mensaje="Sent you a collar!"         # Message when used
)
```

### Item Requirements

For each item, you need:

1. **Image file**: `img_items/item_name.png` (shown in shop catalog)
2. **GIF files**: `gifs_items/item_name/` folder with animation files
   ```
   gifs_items/collar/
   ├── gif1.gif
   ├── gif2.gif
   └── gif3.gif
   ```

3. **Database entry**: Add via `insert_item()` function

### Shop Button Configuration

Update `src/handlers/tienda.py` in `botonera_catalogo()` function:

```python
def botonera_catalogo():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1️⃣ Collar", callback_data="producto_1"),
            InlineKeyboardButton("2️⃣ Whip", callback_data="producto_2"),
            InlineKeyboardButton("3️⃣ Rope", callback_data="producto_3"),
        ],
        [
            InlineKeyboardButton("⬅️ Back to Menu", callback_data="volver_menu")
        ]
    ])
```

## Reward System Configuration

### Points Per Action

Edit `src/handlers/rewards.py`:

```python
REWARD_MULTIMEDIA = 10          # Points for 3 media posts
REWARD_NSFW = 10                # Points for 5 NSFW posts
REWARD_PRESENTATION = 5         # Points for presentation with photo
```

### Edit in `src/handlers/theme_juegosYcasino.py`:

```python
REWARD_DICE_WIN = 50            # Points for rolling 1 or 6
```

### Bet System Parameters

```python
BET_TIMEOUT = 60                # Seconds to accept a bet
MAX_DAILY_GAMES = 5             # Max /jugar uses per day
```

## Security Configuration

### Enable Admin-Only Commands

Check `verificar_admin()` function in handlers before executing sensitive operations.

### Punishment System Configuration

The punishment system uses a JSON file (`castigados.json`) to track punished users:

```json
{
  "-1003290179217": [123456789, 987654321],
  "-1002983018006": [555555555]
}
```

- Users in this list cannot post outside the "theme_rincon" topic
- Only DOM users can punish/forgive their submissives

## Database Configuration

### Database Location

By default, SQLite database (`usuarios.db`) is created in the project root.

To use a custom path:

```
DATABASE_FILE=/custom/path/usuarios.db
```

### Database Initialization

The database is automatically initialized on first run, creating:
- `usuarios_tb` - User accounts and balance
- `items_tb` - Item catalog
- `items_usuarios_tb` - User inventory
- `perfiles_tb` - User profiles

### Database Optimization

Indexes are automatically created on:
- `items_usuarios_tb(id_user)`
- `items_usuarios_tb(id_item)`

For production with large datasets, consider PostgreSQL.

## Logging Configuration

### Log Levels

```
LOG_LEVEL=DEBUG    # Most verbose, includes all operations
LOG_LEVEL=INFO     # Standard operations, errors, important events
LOG_LEVEL=WARNING  # Only warnings and errors
LOG_LEVEL=ERROR    # Only errors
LOG_LEVEL=CRITICAL # Only critical errors
```

### Log Output

Currently, logs are printed to console. For production:

1. Implement file logging:
```python
import logging

logging.basicConfig(
    filename='pibot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

2. Or use external service: Sentry, Datadog, etc.

## Performance Tuning

### Database Connection Pooling

Current implementation creates a new connection per operation. For high load:

```python
# Consider connection pooling
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    try:
        yield conn
    finally:
        conn.close()
```

### Handler Optimization

Reduce database queries by caching frequently accessed data:

```python
# Cache user balance for 5 minutes
cache = {}
cache_ttl = 300  # seconds
```

### Message Processing

Use `drop_pending_updates=True` in production to ignore backlog of messages when bot restarts.

## Webhook Configuration (Advanced)

For alternative to polling (more efficient for hosted environments):

1. Provide public HTTPS endpoint
2. Configure bot to use webhook:
```python
from telegram.ext import Application

app.bot.set_webhook(url="https://yourdomain.com/webhook")
```

3. Implement webhook handler in your web server

[Detailed webhook configuration coming soon]
