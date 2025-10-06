# 🚀 Deployment Guide

This guide covers various deployment options for the Expense Tracker Telegram Bot.

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Telegram Bot Token
- Server/VPS with internet access

## 🐳 Docker Deployment (Recommended)

### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

CMD ["python", "main.py"]
```

### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: expense-tracker-bot
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - DATABASE_URL=postgresql://expense_user:${DB_PASSWORD}@db:5432/expense_tracker
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:13
    container_name: expense-tracker-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=expense_tracker
      - POSTGRES_USER=expense_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  postgres_data:
```

### 3. Create .env file
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
DB_PASSWORD=your_secure_password_here
```

### 4. Deploy
```bash
# Build and start services
docker-compose up -d

# Initialize database
docker-compose exec bot python setup_database.py

# View logs
docker-compose logs -f bot
```

## 🐧 Systemd Deployment (Linux)

### 1. Create systemd service file
```bash
sudo nano /etc/systemd/system/expense-bot.service
```

```ini
[Unit]
Description=Expense Tracker Telegram Bot
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=botuser
Group=botuser
WorkingDirectory=/opt/expense-tracker-bot
ExecStart=/opt/expense-tracker-bot/venv/bin/python main.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/expense-tracker-bot/src
EnvironmentFile=/opt/expense-tracker-bot/.env

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/expense-tracker-bot

[Install]
WantedBy=multi-user.target
```

### 2. Setup deployment
```bash
# Create user
sudo useradd -r -s /bin/false botuser

# Create directory
sudo mkdir -p /opt/expense-tracker-bot
sudo chown botuser:botuser /opt/expense-tracker-bot

# Copy application
sudo cp -r . /opt/expense-tracker-bot/
sudo chown -R botuser:botuser /opt/expense-tracker-bot

# Create virtual environment
cd /opt/expense-tracker-bot
sudo -u botuser python3 -m venv venv
sudo -u botuser venv/bin/pip install -r requirements.txt

# Setup database
sudo -u botuser venv/bin/python setup_database.py

# Enable and start service
sudo systemctl enable expense-bot
sudo systemctl start expense-bot

# Check status
sudo systemctl status expense-bot
```

## ☁️ Cloud Deployment

### AWS EC2
1. Launch EC2 instance (Ubuntu 20.04 LTS)
2. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip postgresql postgresql-contrib nginx
```
3. Setup PostgreSQL:
```bash
sudo -u postgres createdb expense_tracker
sudo -u postgres createuser expense_user
sudo -u postgres psql -c "ALTER USER expense_user PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO expense_user;"
```
4. Deploy application using systemd method above

### DigitalOcean Droplet
1. Create droplet with Ubuntu 20.04
2. Follow systemd deployment steps
3. Configure firewall:
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Heroku
1. Create `Procfile`:
```
worker: python main.py
```
2. Add PostgreSQL addon:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```
3. Set environment variables:
```bash
heroku config:set TELEGRAM_BOT_TOKEN=your_token
```
4. Deploy:
```bash
git push heroku main
```

## 🔧 Production Configuration

### Environment Variables
```env
# Production settings
DEBUG=False
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/expense_tracker

# Bot
TELEGRAM_BOT_TOKEN=your_production_token

# Security
SECRET_KEY=your_secret_key_here
```

### Logging Configuration
Create `logging.conf`:
```ini
[loggers]
keys=root,bot

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_bot]
level=INFO
handlers=fileHandler
qualname=bot
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=simpleFormatter
args=('logs/bot.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Nginx Reverse Proxy (Optional)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring

### Health Check Script
Create `health_check.py`:
```python
import requests
import sys

def check_bot_health():
    try:
        # Check if bot is responding
        # Add your health check logic here
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    if check_bot_health():
        sys.exit(0)
    else:
        sys.exit(1)
```

### Log Rotation
Add to `/etc/logrotate.d/expense-bot`:
```
/opt/expense-tracker-bot/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 botuser botuser
    postrotate
        systemctl reload expense-bot
    endscript
}
```

## 🔒 Security Best Practices

1. **Use strong passwords** for database and system accounts
2. **Keep dependencies updated** regularly
3. **Use environment variables** for sensitive data
4. **Implement rate limiting** for production use
5. **Monitor logs** for suspicious activity
6. **Use HTTPS** for any web interfaces
7. **Regular backups** of database
8. **Firewall configuration** to restrict access

## 📈 Scaling Considerations

### Database Optimization
- Add indexes for frequently queried columns
- Implement connection pooling
- Consider read replicas for heavy reporting

### Bot Scaling
- Implement rate limiting per user
- Add caching for frequently accessed data
- Consider horizontal scaling with load balancer

### Monitoring
- Set up application monitoring (e.g., Prometheus + Grafana)
- Monitor database performance
- Track bot usage metrics

## 🆘 Troubleshooting

### Common Issues

**Service won't start:**
```bash
sudo systemctl status expense-bot
sudo journalctl -u expense-bot -f
```

**Database connection issues:**
```bash
sudo -u postgres psql -c "SELECT 1;"
```

**Permission issues:**
```bash
sudo chown -R botuser:botuser /opt/expense-tracker-bot
```

**Memory issues:**
```bash
free -h
ps aux --sort=-%mem | head
```

### Backup and Recovery
```bash
# Database backup
pg_dump -h localhost -U expense_user expense_tracker > backup.sql

# Restore
psql -h localhost -U expense_user expense_tracker < backup.sql
```

---

For additional support, check the main README.md or open an issue on GitHub.
