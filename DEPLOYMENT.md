# OmniTraffick - Production Deployment Guide

## Prerequisites

- **Server:** Ubuntu 22.04+ or similar (4GB RAM minimum, 8GB recommended)
- **Domain:** ops.omnitraffick.com (or your domain)
- **Services:** PostgreSQL 14+, Redis 7+
- **Node:** 20.x LTS
- **Python:** 3.11+

---

## 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib redis-server nginx certbot python3-certbot-nginx

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Create app user
sudo adduser --system --group omnitraffick
sudo mkdir -p /opt/omnitraffick
sudo chown omnitraffick:omnitraffick /opt/omnitraffick
```

---

## 2. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql << EOF
CREATE DATABASE omnitraffick;
CREATE USER omnitraffick WITH PASSWORD 'CHANGE_THIS_PASSWORD';
ALTER ROLE omnitraffick SET client_encoding TO 'utf8';
ALTER ROLE omnitraffick SET default_transaction_isolation TO 'read committed';
ALTER ROLE omnitraffick SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE omnitraffick TO omnitraffick;
EOF

# Configure Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

---

## 3. Application Deployment

```bash
# Clone repository
cd /opt/omnitraffick
sudo -u omnitraffick git clone https://github.com/isaacbuz/OmniTraffick.git .

# Backend setup
cd /opt/omnitraffick/omnitraffick
sudo -u omnitraffick python3.11 -m venv .venv
sudo -u omnitraffick .venv/bin/pip install -r requirements.txt

# Create .env
sudo -u omnitraffick cat > .env << EOF
# Database
DATABASE_URL=postgresql://omnitraffick:CHANGE_THIS_PASSWORD@localhost:5432/omnitraffick

# Application
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=false
ENVIRONMENT=production

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Meta API
META_ACCESS_TOKEN=your_meta_token
META_AD_ACCOUNT_ID=your_ad_account_id
META_PIXEL_ID=your_pixel_id

# TikTok API
TIKTOK_ACCESS_TOKEN=your_tiktok_token

# Google Ads API
GOOGLE_ADS_CLIENT_ID=your_client_id

# AI (Optional)
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-west1-gcp
EOF

# Run migrations
sudo -u omnitraffick .venv/bin/alembic upgrade head

# Frontend setup
cd /opt/omnitraffick/omnitraffick/frontend
sudo -u omnitraffick npm install
sudo -u omnitraffick npm run build
```

---

## 4. Systemd Services

### FastAPI Backend

```bash
sudo cat > /etc/systemd/system/omnitraffick-api.service << 'EOF'
[Unit]
Description=OmniTraffick FastAPI Backend
After=network.target postgresql.service

[Service]
Type=simple
User=omnitraffick
WorkingDirectory=/opt/omnitraffick/omnitraffick
Environment="PATH=/opt/omnitraffick/omnitraffick/.venv/bin"
ExecStart=/opt/omnitraffick/omnitraffick/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable omnitraffick-api
sudo systemctl start omnitraffick-api
```

### Celery Worker

```bash
sudo cat > /etc/systemd/system/omnitraffick-worker.service << 'EOF'
[Unit]
Description=OmniTraffick Celery Worker
After=network.target redis-server.service

[Service]
Type=simple
User=omnitraffick
WorkingDirectory=/opt/omnitraffick/omnitraffick
Environment="PATH=/opt/omnitraffick/omnitraffick/.venv/bin"
ExecStart=/opt/omnitraffick/omnitraffick/.venv/bin/celery -A src.workers.celery_app worker --loglevel=info --concurrency=4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable omnitraffick-worker
sudo systemctl start omnitraffick-worker
```

### Next.js Frontend

```bash
sudo cat > /etc/systemd/system/omnitraffick-frontend.service << 'EOF'
[Unit]
Description=OmniTraffick Next.js Frontend
After=network.target

[Service]
Type=simple
User=omnitraffick
WorkingDirectory=/opt/omnitraffick/omnitraffick/frontend
Environment="NODE_ENV=production"
Environment="NEXT_PUBLIC_API_URL=https://ops.omnitraffick.com"
Environment="NEXT_PUBLIC_WS_URL=wss://ops.omnitraffick.com"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable omnitraffick-frontend
sudo systemctl start omnitraffick-frontend
```

---

## 5. Nginx Configuration

```bash
sudo cat > /etc/nginx/sites-available/omnitraffick << 'EOF'
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3001;
}

server {
    listen 80;
    server_name ops.omnitraffick.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API docs
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    # Health check
    location /health {
        proxy_pass http://backend;
        access_log off;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/omnitraffick /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 6. SSL Certificate

```bash
sudo certbot --nginx -d ops.omnitraffick.com
```

---

## 7. Monitoring

```bash
# Check service status
sudo systemctl status omnitraffick-api
sudo systemctl status omnitraffick-worker
sudo systemctl status omnitraffick-frontend

# View logs
sudo journalctl -u omnitraffick-api -f
sudo journalctl -u omnitraffick-worker -f
sudo journalctl -u omnitraffick-frontend -f

# Check database
sudo -u postgres psql omnitraffick -c "SELECT COUNT(*) FROM campaigns;"

# Check Redis
redis-cli ping
```

---

## 8. Maintenance

### Update Application

```bash
cd /opt/omnitraffick/omnitraffick
sudo -u omnitraffick git pull
sudo -u omnitraffick .venv/bin/alembic upgrade head
sudo -u omnitraffick cd frontend && npm install && npm run build
sudo systemctl restart omnitraffick-api
sudo systemctl restart omnitraffick-worker
sudo systemctl restart omnitraffick-frontend
```

### Backup Database

```bash
sudo -u postgres pg_dump omnitraffick > omnitraffick_backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
sudo -u postgres psql omnitraffick < omnitraffick_backup_20260227.sql
```

---

## 9. Security Checklist

- [ ] Change all default passwords
- [ ] Configure firewall (UFW): allow 80, 443, 22 only
- [ ] Set up fail2ban for SSH protection
- [ ] Enable PostgreSQL SSL connections
- [ ] Restrict Redis to localhost
- [ ] Set up log rotation
- [ ] Configure automated backups
- [ ] Add monitoring (Datadog, Sentry, etc.)
- [ ] Review and update SECRET_KEY
- [ ] Rotate API tokens regularly

---

## 10. Troubleshooting

**Backend not starting:**
```bash
sudo journalctl -u omnitraffick-api -n 50
# Check .env file, database connection, migrations
```

**Celery not processing tasks:**
```bash
sudo journalctl -u omnitraffick-worker -n 50
# Check Redis connection, Celery broker URL
```

**Frontend build errors:**
```bash
cd /opt/omnitraffick/omnitraffick/frontend
sudo -u omnitraffick npm run build
# Check Node version, dependencies
```

---

**Deployment complete!** Access at https://ops.omnitraffick.com
