# Deployment Guide

Comprehensive guide for deploying PiBot to various platforms.

## Quick Start (Replit)

### 1. Setup Repository on Replit

1. Go to [replit.com](https://replit.com)
2. Click "Create" → "Import from GitHub"
3. Paste your repository URL
4. Click "Import"

Replit will automatically detect it's a Python project.

### 2. Configure Environment Variables

1. Click on "Secrets" (lock icon in sidebar)
2. Add your environment variables:
   ```
   BOT_TOKEN=your_bot_token_here
   DATABASE_FILE=usuarios.db
   LOG_LEVEL=INFO
   ```

Get your `BOT_TOKEN` from [@BotFather](https://t.me/botfather) on Telegram.

### 3. Install Dependencies

The `.replit` file should automatically install dependencies, but you can manually run:

```bash
pip install -r requirements.txt
```

### 4. Run the Bot

```bash
python main.py
```

The bot will start polling for messages immediately.

To run in the background:
1. Click "Run" button in Replit (or `python main.py`)
2. This starts the bot in the foreground
3. Keep the Replit window open or use "Always On" (Pro feature)

### 5. Keep Bot Running 24/7 (Replit Pro)

For Replit Pro users:
1. In project settings, enable "Allow background execution"
2. The bot will continue running even if the browser is closed

For free tier users:
- The bot runs while Replit project is open
- Close the project to stop the bot

## Heroku Deployment

### Prerequisites
- Heroku account
- Heroku CLI installed
- Git repository initialized

### Steps

1. **Create Heroku App**:
```bash
heroku login
heroku create your-app-name
```

2. **Set Environment Variables**:
```bash
heroku config:set BOT_TOKEN=your_token
heroku config:set DATABASE_FILE=usuarios.db
```

3. **Deploy Code**:
```bash
git push heroku main
```

4. **Enable Worker Dyno**:
```bash
heroku ps:scale worker=1
```

5. **View Logs**:
```bash
heroku logs --tail
```

### Notes for Heroku
- **Procfile** is already configured: `worker: python main.py`
- Database persists in temporary storage (files deleted on dyno restart)
- Consider using PostgreSQL add-on for persistent storage

## Docker Deployment

### Build Docker Image

Create a `Dockerfile` in project root:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 pibot
USER pibot

# Run bot
CMD ["python", "main.py"]
```

### Build & Run

```bash
# Build image
docker build -t pibot:latest .

# Run container
docker run -e BOT_TOKEN=your_token pibot:latest

# Run with volume mount for database
docker run -e BOT_TOKEN=your_token \
           -v pibot_data:/app \
           pibot:latest
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  pibot:
    build: .
    environment:
      BOT_TOKEN: ${BOT_TOKEN}
      DATABASE_FILE: usuarios.db
      LOG_LEVEL: INFO
    volumes:
      - pibot_data:/app
    restart: unless-stopped

volumes:
  pibot_data:
```

Run with:
```bash
docker-compose up -d
```

## VPS/Traditional Server Deployment

###  Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- systemd for process management

### Setup

1. **SSH into server**:
```bash
ssh user@your.server.ip
```

2. **Clone repository**:
```bash
git clone https://github.com/yourusername/PiBot2.0.git
cd PiBot2.0
```

3. **Create Python virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Create .env file**:
```bash
cp .env.example .env
nano .env  # Edit with your token
```

6. **Test run**:
```bash
python main.py
```

Should output: `🤖 PiBot iniciado e listo para recibir mensajes...`

### Setup Systemd Service

Create `/etc/systemd/system/pibot.service`:

```ini
[Unit]
Description=PiBot Telegram Bot
After=network.target

[Service]
Type=simple
User=pibot
WorkingDirectory=/home/pibot/PiBot2.0
Environment="PATH=/home/pibot/PiBot2.0/venv/bin"
ExecStart=/home/pibot/PiBot2.0/venv/bin/python main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:

```bash
# Enable and start service
sudo systemctl enable pibot
sudo systemctl start pibot

# Check status
sudo systemctl status pibot

# View logs
sudo journalctl -u pibot -f
```

## AWS Lambda Deployment

For serverless deployment using API Gateway and Lambda:

1. Install serverless framework
2. Use asyncio-based handler
3. Store database in S3 or RDS
4. Use API Gateway webhooks instead of polling

[Detailed Lambda guide coming soon]

## Deployment Checklist

Before deploying to production:

- [ ] `.env` file created with correct token
- [ ] All tests passing locally
- [ ] Code formatted and linted
- [ ] `requirements.txt` up to date
- [ ] Database initialized and working
- [ ] Bot tested in test group
- [ ] All commands and handlers working
- [ ] No hardcoded secrets in code
- [ ] `.gitignore` prevents secret leakage
- [ ] Backup of production database exists
- [ ] Error handling and logging configured
- [ ] Monitoring alerts set up (if applicable)

## Monitoring & Maintenance

### Viewing Logs

**Replit**: Click "Logs" tab in editor

**Heroku**: `heroku logs --tail`

**Docker**: `docker logs <container_id>`

**Systemd**: `sudo journalctl -u pibot -f`

### Database Backup

```bash
# SQLite backup
cp usuarios.db usuarios.db.backup.$(date +%Y%m%d)

# Or use automated backups
crontab -e
# Add: 0 2 * * * cp /path/to/usuarios.db /backups/usuarios.db.$(date +\%Y\%m\%d)
```

### Updating Code

```bash
# Pull latest changes
git pull origin main

# Restart bot
systemctl restart pibot  # Or redeploy on Replit/Heroku
```

### Troubleshooting Deployment Issues

**Bot not starting**:
- Check `BOT_TOKEN` in environment variables
- Verify Python version: `python --version`
- Check logs for error messages

**Database errors**:
- Ensure database file has correct permissions
- Check disk space on server
- Verify database isn't corrupted: `sqlite3 usuarios.db "PRAGMA integrity_check;"`

**Memory issues**:
- Monitor with `top` or `htop`
- Consider reducing inactive timeout for cleanup
- Check for memory leaks in handlers

**Slow responses**:
- Check database indexes
- Consider caching frequently accessed data
- Profile with Python profiler

## Production Recommendations

1. **Use PostgreSQL instead of SQLite** for production
2. **Enable HTTPS** if using webhooks
3. **Implement rate limiting** for expensive operations
4. **Set up monitoring** (Sentry, Datadog, New Relic)
5. **Configure log aggregation** (ELK Stack, Splunk)
6. **Regular security audits** of dependencies
7. **Backup strategy** for user data
8. **Load balancing** if expecting high traffic
