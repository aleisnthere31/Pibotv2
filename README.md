# PiBot 2.0

A comprehensive Telegram bot for community management with gamification features, including a virtual economy system, item shop, and punitive measures for community moderation.

## Features

- **Virtual Economy**: Users earn and spend PiPesos through activities and transactions.
- **Gamification System**: Games, bets, and rewards for participation.
- **Item Inventory**: Shop system where users can purchase and use items.
- **Automatic Rewards**: Earn virtual currency for media posts, presentations, and participation.
- **User Management**: Profile system with support for multiple communities.
- **Punishment System**: DOM (Dominant) users can temporarily restrict other users to a designated "punishment corner".
- **Multiple Communities**: Support for managing multiple Telegram communities with different configurations.

## Technology Stack

- **Framework**: aiogram 3.22.0 (async Telegram bot framework)
- **Database**: SQLite3
- **Language**: Python 3.8+
- **Deployment**: Replit (compatible with other platforms)

## Project Structure

```
PiBot2.0/
├── src/                           # Main source code
│   ├── config/                    # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py            # Bot settings and community configs
│   ├── database/                  # Database operations
│   │   ├── __init__.py
│   │   └── database.py            # SQLite management
│   ├── handlers/                  # Command and event handlers
│   │   ├── __init__.py
│   │   ├── general.py             # General commands (/ver, /dar, etc.)
│   │   ├── starting_menu.py       # /start menu
│   │   ├── inventario.py          # Inventory management
│   │   ├── tienda.py              # Shop system
│   │   ├── theme_juegosYcasino.py # Games and betting
│   │   ├── rewards.py             # Reward system
│   │   └── welcoming.py           # Welcome messages
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py
│   │   └── helpers.py             # Helper functions
│   └── __init__.py
├── gifs_items/                    # Item GIF animations
├── img_items/                     # Item images
├── docs/                          # Documentation
├── tests/                         # Unit tests
├── main.py                        # Bot entry point
├── config.py                      # Legacy config (being migrated)
├── sqlgestion.py                  # Legacy database (being migrated)
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── procfile                       # Heroku deployment config
└── README.md                      # This file
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/PiBot2.0.git
cd PiBot2.0
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and add your bot token from [BotFather](https://t.me/botfather):

```
BOT_TOKEN=your_bot_token_here
DATABASE_FILE=usuarios.db
LOG_LEVEL=INFO
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or with conda:

```bash
conda create -n pibot python=3.10
conda activate pibot
pip install -r requirements.txt
```

### 4. Initialize Database

The database is automatically initialized on first run.

## Running the Bot

### Local Development

```bash
python main.py
```

### Replit Deployment

1. Connect your GitHub repository to Replit
2. Configure the environment variables in Replit secrets
3. Run the bot directly or use a background process

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t pibot .
docker run -e BOT_TOKEN=your_token pibot
```

## Configuration

### Community Setup

Edit `src/config/settings.py` to add or modify communities:

```python
COMUNIDADES = [
    {
        "id_comunidad": -1003290179217,  # Chat ID
        "nombre": "Your Community Name",
        "temas": {
            "theme_name": topic_id,
            "theme_another": another_id,
            ...
        }
    }
]
```

### Admin Setup

Configure administrators per community in `settings.py`:

```python
ADMINS = [
    {
        "id_comunidad": -1003290179217,
        "admins": {user_id1, user_id2, ...}
    }
]
```

## Available Commands

### General Commands

- `/start` - Open main menu (private chat only)
- `/ver` - Check your PiPesos balance
- `/dar <amount> [@user]` - Transfer PiPesos to another user
- `/regalar <amount> [@user]` - Admin: Gift PiPesos
- `/NumAzar <n1> <n2>` - Generate random number between n1 and n2

### Economy Commands

- `/tienda` - Open the shop
- `/inventario` - View your items
- `/usar <item>` - Use an item on someone

### Games & Betting

- `/apostar <amount>` - Create a betting pool
- `/aceptar` - Accept a bet
- `/cancelar` - Cancel your bet
- `/jugar` - Roll a dice (max 5 times/day, win with 1 or 6 = +50 points)
- `/robar @user` - Try to steal PiPesos from someone

### Admin Commands

- `/castigar @user` - Confine user to punishment corner (DOM users only)
- `/perdonar @user` - Release user from punishment
- `/quitar <amount> @user` - Remove PiPesos from user

## Database Schema

### usuarios_tb
- `id_user` (INTEGER PRIMARY KEY): Telegram user ID
- `saldo` (INTEGER): User's PiPesos balance

### items_tb
- `id_item` (INTEGER PRIMARY KEY): Item ID
- `nombre` (TEXT): Item name
- `precio` (INTEGER): Price in PiPesos
- `imagen` (TEXT): Image file path
- `descripcion` (TEXT): Item description
- `mensaje` (TEXT): Custom message when used

### items_usuarios_tb
- `id` (INTEGER PRIMARY KEY): Relationship ID
- `id_user` (INTEGER FOREIGN KEY): User ID
- `id_item` (INTEGER FOREIGN KEY): Item ID
- `cantidad` (INTEGER): Item quantity

### perfiles_tb
- `id_user` (INTEGER PRIMARY KEY): User ID
- `username` (TEXT): Telegram username
- `nombre` (TEXT): Display name
- `rol` (TEXT): User role
- `orientacion_sexual` (TEXT): User preference
- `genero` (TEXT): User gender
- `ubicacion` (TEXT): User location
- `edad` (INTEGER): User age

## Reward System

Users earn PiPesos through various activities:

- **Multimedia posts** (3 items): +10 PiPesos
- **NSFW posts** (5 items): +10 PiPesos
- **Presentation with photo**: +5 PiPesos (one-time)
- **Successful dice roll** (1 or 6): +50 PiPesos
- **Winning bets**: Bet amount

## Troubleshooting

### Bot not responding
1. Check if `BOT_TOKEN` is correctly set in `.env`
2. Verify the bot has permission to read messages in the group
3. Check logs: `tail -f logs/pibot.log`

### Database errors
1. Ensure `usuarios.db` database file has write permissions
2. Try deleting the database to reinitialize: `rm usuarios.db`
3. Run `python -c "from src.database import create_database, create_tables; create_database(); create_tables()"`

### Permission errors
1. Verify user IDs in `ADMINS` and `DOMS` configuration
2. Check that the bot has admin rights in the community

## Development

### Code Quality

Run linting and formatting:

```bash
black src/
flake8 src/
```

### Testing

Run unit tests:

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## Security Notes

- **NEVER commit `.env` file** to version control
- Store sensitive data only in environment variables
- Use strong, unique BOT_TOKEN values
- Regularly update dependencies for security patches

## License

This project is provided as-is. Modify and use as needed for your community.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Version**: 2.0.0  
**Last Updated**: 2026-03-13
