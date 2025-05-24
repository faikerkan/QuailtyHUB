# 🚀 CallQualityHub Deployment Kılavuzu

Bu kılavuz, CallQualityHub uygulamasını production ortamında nasıl deploy edeceğinizi açıklar.

## 📋 İçerik

- [Genel Bakış](#genel-bakış)
- [Sunucu Gereksinimleri](#sunucu-gereksinimleri)
- [Docker ile Deployment](#docker-ile-deployment)
- [Manuel Deployment](#manuel-deployment)
- [Nginx Konfigürasyonu](#nginx-konfigürasyonu)
- [SSL Sertifikası](#ssl-sertifikası)
- [Monitoring ve Logging](#monitoring-ve-logging)
- [Backup Stratejisi](#backup-stratejisi)
- [Güvenlik](#güvenlik)

## 🎯 Genel Bakış

CallQualityHub, production ortamında aşağıdaki bileşenlerle çalışır:

```
Internet → Nginx → Gunicorn → Django App → PostgreSQL
                 ↓
            Static Files (Nginx)
                 ↓
            Media Files (Nginx)
```

## 💻 Sunucu Gereksinimleri

### Minimum Gereksinimler
- **CPU**: 2 vCPU
- **RAM**: 4 GB
- **Disk**: 50 GB SSD
- **OS**: Ubuntu 20.04 LTS veya daha yeni

### Önerilen Gereksinimler
- **CPU**: 4 vCPU
- **RAM**: 8 GB
- **Disk**: 100 GB SSD
- **OS**: Ubuntu 22.04 LTS

### Yazılım Gereksinimleri
```bash
# Temel sistem güncellemesi
sudo apt update && sudo apt upgrade -y

# Gerekli paketler
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    supervisor \
    git \
    curl \
    certbot \
    python3-certbot-nginx
```

## 🐳 Docker ile Deployment

### 1. Dockerfile Oluşturma

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodları
COPY . .

# Collectstatic
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "call_quality_hub.wsgi:application"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: qualityhub
      POSTGRES_USER: qualityhubuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://qualityhubuser:${DB_PASSWORD}@db:5432/qualityhub
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - db

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### 3. Docker Deployment Komutları

```bash
# .env dosyasını oluşturun
cp .env-sample .env
# .env dosyasını production değerleri ile düzenleyin

# Docker Compose ile başlatın
docker-compose up -d

# Migrate işlemleri
docker-compose exec web python manage.py migrate

# Süper kullanıcı oluşturun
docker-compose exec web python manage.py createsuperuser
```

## 🔧 Manuel Deployment

### 1. Kullanıcı ve Dizin Hazırlığı

```bash
# Deploy kullanıcısı oluşturun
sudo adduser deploy
sudo usermod -aG sudo deploy

# Proje dizini
sudo mkdir -p /var/www/callqualityhub
sudo chown deploy:deploy /var/www/callqualityhub
```

### 2. Kod Deploy

```bash
# Deploy kullanıcısına geçin
sudo su - deploy

# Kodu çekin
git clone https://github.com/username/callqualityhub.git /var/www/callqualityhub
cd /var/www/callqualityhub

# Sanal ortam oluşturun
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 3. PostgreSQL Kurulumu

```bash
# PostgreSQL kullanıcısına geçin
sudo -u postgres psql

-- Veritabanı ve kullanıcı oluşturun
CREATE DATABASE qualityhub;
CREATE USER qualityhubuser WITH PASSWORD 'güçlü_şifre_buraya';
ALTER ROLE qualityhubuser SET client_encoding TO 'utf8';
ALTER ROLE qualityhubuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE qualityhubuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE qualityhub TO qualityhubuser;
\q
```

### 4. Django Konfigürasyonu

```bash
# Environment dosyası
cp .env-sample .env
nano .env

# Migration ve static files
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 5. Gunicorn Konfigürasyonu

```bash
# Gunicorn yapılandırma dosyası
cat > /var/www/callqualityhub/gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
user = "deploy"
group = "deploy"
chdir = "/var/www/callqualityhub"
pythonpath = "/var/www/callqualityhub"
raw_env = ["DJANGO_SETTINGS_MODULE=call_quality_hub.settings"]
EOF
```

### 6. Supervisor Konfigürasyonu

```bash
# Supervisor konfigürasyonu
sudo cat > /etc/supervisor/conf.d/callqualityhub.conf << EOF
[program:callqualityhub]
command=/var/www/callqualityhub/venv/bin/gunicorn -c /var/www/callqualityhub/gunicorn.conf.py call_quality_hub.wsgi:application
directory=/var/www/callqualityhub
user=deploy
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/callqualityhub.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
EOF

# Supervisor'ı yeniden başlatın
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start callqualityhub
```

## 🌐 Nginx Konfigürasyonu

```nginx
# /etc/nginx/sites-available/callqualityhub
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Sertifikaları
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL Güvenlik Ayarları
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Güvenlik Headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    # Dosya boyutu limiti
    client_max_body_size 100M;

    # Static dosyalar
    location /static/ {
        alias /var/www/callqualityhub/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media dosyalar
    location /media/ {
        alias /var/www/callqualityhub/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Ana uygulama
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

```bash
# Site'ı aktifleştir
sudo ln -s /etc/nginx/sites-available/callqualityhub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 SSL Sertifikası

### Let's Encrypt ile Ücretsiz SSL

```bash
# Certbot ile SSL sertifikası
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Otomatik yenileme testini yapın
sudo certbot renew --dry-run
```

### Otomatik Yenileme

```bash
# Crontab ekleyin
sudo crontab -e

# Aşağıdaki satırı ekleyin
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring ve Logging

### 1. Log Dosyaları

```bash
# Uygulama logları
tail -f /var/log/callqualityhub.log

# Nginx logları
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# PostgreSQL logları
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### 2. System Monitoring

```bash
# Sistem kaynak kullanımı
htop

# Disk kullanımı
df -h

# Network bağlantıları
ss -tulpn

# Supervisor durumu
sudo supervisorctl status
```

### 3. Application Health Check

```python
# health_check.py
import requests
import sys

try:
    response = requests.get('https://your-domain.com/health/', timeout=10)
    if response.status_code == 200:
        print("✅ Application is healthy")
        sys.exit(0)
    else:
        print(f"❌ Application returned {response.status_code}")
        sys.exit(1)
except requests.RequestException as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)
```

## 💾 Backup Stratejisi

### 1. Veritabanı Backup

```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/var/backups/callqualityhub"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="qualityhub"
DB_USER="qualityhubuser"

mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Gzip ile sıkıştır
gzip $BACKUP_DIR/db_backup_$DATE.sql

# 30 günden eski backupları sil
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Database backup completed: db_backup_$DATE.sql.gz"
```

### 2. Media Dosyaları Backup

```bash
#!/bin/bash
# backup_media.sh

BACKUP_DIR="/var/backups/callqualityhub"
DATE=$(date +%Y%m%d_%H%M%S)
MEDIA_DIR="/var/www/callqualityhub/media"

mkdir -p $BACKUP_DIR

# Media dosyalarını tar ile arşivle
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C $MEDIA_DIR .

# 30 günden eski backupları sil
find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +30 -delete

echo "Media backup completed: media_backup_$DATE.tar.gz"
```

### 3. Otomatik Backup

```bash
# Crontab ile otomatik backup
sudo crontab -e

# Her gece 2:00'de veritabanı backup
0 2 * * * /var/www/callqualityhub/scripts/backup_db.sh

# Her gece 3:00'de media backup
0 3 * * * /var/www/callqualityhub/scripts/backup_media.sh
```

## 🛡️ Güvenlik

### 1. Firewall Konfigürasyonu

```bash
# UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

### 2. Fail2Ban

```bash
# Fail2Ban kurulumu
sudo apt install fail2ban

# Nginx için konfigürasyon
sudo cat > /etc/fail2ban/jail.local << EOF
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF

sudo systemctl restart fail2ban
```

### 3. Regular Security Updates

```bash
#!/bin/bash
# security_updates.sh

# Sistem güncellemeleri
sudo apt update
sudo apt upgrade -y

# Python paket güncellemeleri
cd /var/www/callqualityhub
source venv/bin/activate
pip list --outdated
pip install --upgrade $(pip list --outdated --format=freeze | cut -d= -f1)

echo "Security updates completed"
```

## 🔄 Deploy Scripti

```bash
#!/bin/bash
# deploy.sh

set -e

PROJECT_DIR="/var/www/callqualityhub"
BACKUP_DIR="/var/backups/callqualityhub"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🚀 Starting deployment..."

# Backup veritabanı
echo "📦 Creating database backup..."
mkdir -p $BACKUP_DIR
pg_dump -U qualityhubuser -h localhost qualityhub > $BACKUP_DIR/pre_deploy_$DATE.sql

# Kodu güncelle
echo "📥 Pulling latest code..."
cd $PROJECT_DIR
git pull origin main

# Virtual environment aktifleştir
source venv/bin/activate

# Bağımlılıkları güncelle
echo "📦 Updating dependencies..."
pip install -r requirements.txt

# Migration
echo "🔄 Running migrations..."
python manage.py migrate

# Static dosyalar
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Uygulamayı yeniden başlat
echo "🔄 Restarting application..."
sudo supervisorctl restart callqualityhub

echo "✅ Deployment completed successfully!"
```

## 🆘 Troubleshooting

### Yaygın Sorunlar

1. **Application başlamıyor**
   ```bash
   sudo supervisorctl status callqualityhub
   sudo tail -f /var/log/callqualityhub.log
   ```

2. **Static dosyalar yüklenmiyor**
   ```bash
   python manage.py collectstatic --noinput
   sudo nginx -t && sudo systemctl reload nginx
   ```

3. **Database bağlantı sorunu**
   ```bash
   sudo systemctl status postgresql
   psql -U qualityhubuser -h localhost qualityhub
   ```

4. **SSL sertifikası sorunu**
   ```bash
   sudo certbot certificates
   sudo nginx -t
   ```

---

Bu kılavuzla CallQualityHub'ı başarılı bir şekilde production ortamında deploy edebilirsiniz. Herhangi bir sorunla karşılaştığınızda, lütfen GitHub Issues sayfasından destek alın. 