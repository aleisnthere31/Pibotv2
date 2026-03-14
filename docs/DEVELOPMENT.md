# Development Guide

## Getting Started with Development

### Setup Development Environment

1. **Clone and Setup**:
```bash
git clone <repository-url>
cd PiBot2.0
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

2. **Install Development Dependencies**:
```bash
pip install -r requirements.txt
pip install black flake8 pytest pytest-mock mypy
```

3. **Create .env File**:
```bash
cp .env.example .env
# Edit .env with your BOT_TOKEN
```

## Code Style Guide

### Python Formatting

Use Black for code formatting:
```bash
black src/ --line-length=100
```

### Linting

Check code quality with flake8:
```bash
flake8 src/ --max-line-length=100
```

### Type Hints

Use type hints for better IDE support and maintainability:
```python
def process_user(user_id: int, amount: float) -> bool:
    """Process user transaction."""
    pass
```

### Docstrings

Use Google-style docstrings:
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed, explaining behavior,
    edge cases, or important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When X condition occurs
    """
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_database.py::test_user_creation
```

### Writing Tests

Create test files in `tests/` directory:

```python
# tests/test_database.py
import pytest
from src.database import insert_user, get_campo_usuario

class TestUserDatabaseOps:
    
    def test_insert_user(self):
        """Test user creation."""
        result = insert_user(12345, saldo=0, username="testuser", nombre="Test User")
        assert result is True
    
    def test_get_nonexistent_user(self):
        """Test retrieving non-existent user returns None."""
        result = get_campo_usuario(99999, "nombre")
        assert result is None
```

## Adding New Features

### Adding a New Command

1. **Create handler function** in appropriate file:
```python
# In src/handlers/general.py
async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mycommand."""
    await update.message.reply_text("Hello!")
```

2. **Register in main.py**:
```python
from handlers.general import my_command

app.add_handler(CommandHandler("mycommand", my_command), group=0)
```

### Adding a New Item

1. **Add to database**:
```python
from src.database import insert_item

insert_item(
    nombre="Mi Item",
    precio=50,
    ruta_imagen="img_items/miitem.png",
    descripcion="Item awesome description",
    mensaje="Usar este item mola!"
)
```

2. **Add image and GIFs**:
```
img_items/miitem.png          # Catalog image
gifs_items/mi_item/           # GIF folder
    ├── gif1.gif
    ├── gif2.gif
    └── gif3.gif
```

3. **Update shop buttons** in `src/handlers/tienda.py`:
```python
def botonera_catalogo():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("X️⃣ Mi Item", callback_data="producto_7"),
        ],
    ])
```

## Database Migrations

For schema changes:

1. **Backup existing database**:
```bash
cp usuarios.db usuarios.db.backup
```

2. **Make schema changes** in `src/database/database.py` in `create_tables()`

3. **Recreate database**:
```python
from src.database import create_database, create_tables

# Backup old data first!
create_database()
create_tables()
```

## Debugging

### Enable Debug Logging

Set in `.env`:
```
LOG_LEVEL=DEBUG
```

### Telegram Debug Mode

Get detailed message info with `/id` command:
```
/id
→ Chat ID: -1003290179217
  Topic ID: 528
```

### Database Inspection

Query database directly:
```bash
sqlite3 usuarios.db
sqlite> SELECT * FROM usuarios_tb;
sqlite> SELECT COUNT(*) FROM items_usuarios_tb;
```

## Common Tasks

### Add a New Community

Edit `src/config/settings.py`:
```python
COMUNIDADES = [
    ...,
    {
        "id_comunidad": -1004567890123,  # New community
        "nombre": "New Community",
        "temas": {
            "theme_general": 1,
            "theme_games": 2,
            ...
        }
    }
]
```

### Change Reward Amounts

Edit handler files:
```python
# In src/handlers/rewards.py
REWARD_MULTIMEDIA = 10  # PiPesos
REWARD_NSFW = 10
REWARD_PRESENTATION = 5
```

### Update Economy Parameters

In `src/handlers/theme_juegosYcasino.py`:
```python
MAX_BET_AMOUNT = 1000  # Max PiPesos per bet
BET_TIMEOUT = 60  # Seconds to accept bet
```

## Troubleshooting Development Issues

### ImportError: No module named 'src'

Make sure you're running from project root:
```bash
cd PiBot2.0
python main.py
```

### Database locked error

SQLite locks during concurrent writes. Ensure only one bot instance runs.

### Stale module imports

Restart the Python interpreter:
```bash
# Restart terminal or
python -m importlib.reload()
```

## Performance Profiling

### Memory Usage

```python
import tracemalloc

tracemalloc.start()
# ... run code ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current/1024/1024:.1f} MB; Peak: {peak/1024/1024:.1f} MB")
```

### Execution Time

```python
import time

start = time.perf_counter()
# ... operation ...
elapsed = time.perf_counter() - start
print(f"Took {elapsed:.3f} seconds")
```

## Deployment Checklist

Before deploying to production:

- [ ] All tests passing: `pytest tests/`
- [ ] Code formatted: `black src/`
- [ ] Linting passes: `flake8 src/`
- [ ] No hardcoded secrets in code
- [ ] `.env` file NOT committed to git
- [ ] `.env.example` updated if new variables added
- [ ] `requirements.txt` updated: `pip freeze > requirements.txt`
- [ ] Bot tested in test group
- [ ] All commands working
- [ ] Permissions verified
- [ ] Database backup created

## Getting Help

- Check existing issues on GitHub
- Review logs: `python -u main.py 2>&1 | tee bot.log`
- Test in private chat first
- Ask in development discussions
