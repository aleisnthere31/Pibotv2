# Architecture Documentation

## Overview

PiBot is built using a modular, handler-based architecture that leverages the aiogram framework for Telegram bot development. All code is organized into logical packages with clear separation of concerns.

## Core Architecture

### Layered Structure

```
┌─────────────────────────────────────────────────────────┐
│                    main.py (Entry Point)                │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│    Handler Routing (Commands, Callbacks, Messages)      │
│  ├── general.py        (Commands: /ver, /dar, etc.)     │
│  ├── starting_menu.py  (/start and menu navigation)     │
│  ├── inventario.py     (Inventory browsing)             │
│  ├── tienda.py         (Shopping system)                │
│  ├── theme_juegosYcasino.py (Games and betting)        │
│  ├── rewards.py        (Auto-reward system)             │
│  └── welcoming.py      (New member greeting)            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  Utilities & Services                    │
│  ├── Database Operations (src/database/)                │
│  ├── Configuration (src/config/)                        │
│  └── Helper Functions (src/utils/)                      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│            SQLite Database & System Resources            │
└─────────────────────────────────────────────────────────┘
```

## Handler Organization

Each handler file represents a specific feature or command group:

### general.py
**Purpose**: Core economic commands  
**Commands**:
- `/ver` - Balance inquiry
- `/dar` - Transfer funds
- `/regalar` - Admin gift
- `/quitar` - Admin removal
- `/NumAzar` - Random number generator

**Key Functions**:
- `verificar_admin()` - Check admin status
- `obtener_gif_aleatorio()` - Random GIF selection
- `get_receptor()` - Extract target user from message

### starting_menu.py
**Purpose**: Main menu and user entry point  
**Features**:
- `/start` command handler
- Menu button navigation
- Callback routing

**Key Functions**:
- `start()` - Main menu display
- `menu_callback()` - Menu interactions

### tienda.py
**Purpose**: Shop and item purchasing  
**Features**:
- Catalog display with images
- Item details and pricing
- Purchase transactions
- Inventory updates

**Key Functions**:
- `tienda()` - Shop main display
- `tienda_callback()` - Shop interactions
- `comprar_item()` - Purchase logic
- `mostrar_item()` - Item details

### inventario.py
**Purpose**: User inventory management  
**Features**:
- Paginated item browsing
- Item usage (`/usar`)
- GIF animation sending

**Key Functions**:
- `inventario()` - Display inventory with pagination
- `inventario_callback()` - Pagination controls
- `usar()` - Use item on another user

### theme_juegosYcasino.py
**Purpose**: Games and betting system  
**Features**:
- Dice betting (`/apostar`, `/aceptar`, `/cancelar`)
- Automatic game resolution
- Dice roll detection (`/jugar`)
- Theft attempts (`/robar`)

**Key Functions**:
- `apostar()` - Create bet pool
- `aceptar()` - Accept bet
- `detectar_dado()` - Process dice rolls
- `robar()` - Theft mechanics

**In-Memory Data Structures**:
```python
active_bets = {
    thread_id: {
        "apostador_id": int,
        "apostador_username": str,
        "rival_id": int,
        "rival_username": str,
        "cantidad": int,
        "dados": {"apostador": int, "rival": int},
        "activa": bool
    }
}
```

### rewards.py
**Purpose**: Automatic reward distribution  
**Features**:
- Multimedia post rewards
- NSFW content rewards
- Presentation rewards
- Automatic point distribution

**Key Functions**:
- `manejar_imagenes()` - Central image handler
- `detectar_imagenes_multimedia()` - Media rewards
- `detectar_imagenes_nsfw()` - NSFW rewards
- `detectar_imagen_presentacion()` - Intro rewards

### welcoming.py
**Purpose**: New member onboarding  
**Features**:
- Welcome messages
- Presentation deadline verification
- Automatic notifications

**Key Functions**:
- `nuevo_usuario()` - New member greeting
- `mensaje_de_presentaciones()` - Presentation message
- `verificar_presentacion()` - Async deadline check

## Database Module (src/database/)

Centralized database operations with proper connection management.

### Connection Pool
```python
def _get_connection():
    return sql.connect(DATABASE_FILE)
```

### Operation Categories

**User Management**:
- `insert_user()` - Create new user
- `get_campo_usuario()` - Retrieve user field
- `update_perfil()` - Update profile

**Balance Management**:
- `update_saldo()` - Set balance
- `dar_puntos()` - Add points
- `quitar_puntos()` - Remove points

**Item Management**:
- `insert_item()` - Add item to catalog
- `get_campo_item()` - Retrieve item data
- `update_item()` - Modify item

**Inventory Management**:
- `insert_user_item()` - Add item to inventory
- `get_items()` - List user items
- `get_cantidad_item_inventario()` - Check count
- `update_cantidad()` - Modify count

**Utilities**:
- `normalizar_nombre()` - Clean user names
- `to_plain_text()` - Remove accents/special chars
- `reemplazar_acentos()` - Accent replacement

## Configuration Module (src/config/)

Manages all bot settings and sensitive data.

### settings.py

**Environment Variables**:
- `BOT_TOKEN` - Telegram API token
- `DATABASE_FILE` - Database path
- `LOG_LEVEL` - Logging verbosity

**Community Configuration**:
```python
COMUNIDADES = [
    {
        "id_comunidad": int,
        "nombre": str,
        "temas": {
            "theme_name": int,  # topic ID
            ...
        }
    }
]
```

**Admin & DOM Lists**:
```python
ADMINS = [
    {
        "id_comunidad": int,
        "admins": {user_id, ...}
    }
]

DOMS = {
    dom_id: [submissive_ids, ...]
}
```

**Helper Functions**:
- `obtener_temas_por_comunidad()` - Get topic map
- `obtener_admins_comunidad()` - Get admin list

## Data Flow Examples

### User Balance Transfer

```
/dar 50 @recipient
      ↓
dar() handler
      ↓
get_receptor() → extract user ID
      ↓
get_campo_usuario() → verify sender balance
      ↓
quitar_puntos(sender, 50)
dar_puntos(recipient, 50)
      ↓
"Successfully transferred" message
```

### Shopping Flow

```
/tienda
      ↓
tienda() → show catalog image
      ↓
User clicks "Comprar" button
      ↓
tienda_callback() → comprar_item()
      ↓
Verify user balance
      ↓
quitar_puntos() → reduce balance
insert_user_item() → add to inventory
      ↓
Confirmation message
```

### Bet Resolution

```
/apostar 100
      ↓
apostar() → store in active_bets[thread_id]
      ↓
/aceptar
      ↓
aceptar() → add rival_id to active_bets
      ↓
Users roll dice 🎲
      ↓
detectar_dado() → records result
      ↓
When both dice recorded → determine winner
      ↓
dar_puntos(winner) + quitar_puntos(loser)
      ↓
Clear active_bets[thread_id]
```

## Key Design Patterns

### 1. Handler Grouping
Commands are registered in priority groups:
```python
app.add_handler(CommandHandler("start", start), group=0)
app.add_handler(CommandHandler("jugar", jugar), group=1)
app.add_handler(MessageHandler(...), group=6)
```

### 2. Callback Pattern
InlineKeyboardButtons use callback_data for state management:
```python
InlineKeyboardButton("Comprar", callback_data=f"comprar_{item_id}")
```

### 3. Async Processing
Long operations use asyncio.create_task:
```python
asyncio.create_task(auto_cancel())  # 60-second timeout
```

### 4. In-Memory State
Transient data (active bets) stored in module-level dicts:
```python
active_bets = {}  # Cleared on bot restart
```

## Security Considerations

1. **Token Management**: Never hardcode tokens; use environment variables
2. **Admin Verification**: Check permissions before sensitive operations
3. **Input Validation**: Normalize and validate all user inputs
4. **SQL Injection Prevention**: Always use prepared statements
5. **Rate Limiting**: Consider adding cooldowns for resource-intensive operations

## Performance Optimizations

1. **Database Indexes**: Inventory queries indexed on (id_user, id_item)
2. **Connection Pooling**: Single sqlite3 connection per operation
3. **Message Caching**: Avoid repeated database queries in callbacks
4. **Async Operations**: Image resizing, long storage operations async

## Future Architecture Improvements

1. Redis for caching active bets and user state
2. PostgreSQL for production (vs SQLite)
3. Task queue (Celery) for scheduled rewards
4. Dedicated logging system
5. API layer for external integrations
6. Webhook support instead of polling
