# 📞 CallQualityHub - Premium Çağrı Kalite Yönetim Sistemi

<div align="center">

![CallQualityHub](docs/images/dashboard-preview.png)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org/)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Modern, güvenli ve kullanıcı dostu çağrı merkezi kalite değerlendirme sistemi**

[Demo](#demo) • [Kurulum](#kurulum) • [Kullanım](#kullanım) • [API](#api-dokümantasyonu) • [Katkıda Bulunma](#katkıda-bulunma)

</div>

## ✨ Özellikler

### 🎯 Ana Özellikler
- **Rol Tabanlı Erişim**: Admin, Kalite Uzmanı ve Temsilci rolleri
- **Ses Dosyası Yönetimi**: Çağrı kayıtlarını yükleme ve organize etme
- **Dinamik Değerlendirme Formları**: Özelleştirilebilir değerlendirme kriterleri
- **Gerçek Zamanlı Raporlama**: Detaylı analytics ve performans metrikleri
- **REST API**: Tam özellikli API desteği

### 🎨 Kullanıcı Deneyimi
- **Modern UI/UX**: Glassmorphism tasarım dili
- **Responsive Design**: Tüm cihazlarda mükemmel görünüm
- **Dark Theme**: Göz dostu karanlık tema
- **Premium Animasyonlar**: Akıcı geçişler ve hover efektleri

### 🔒 Güvenlik
- **JWT Authentication**: Güvenli kimlik doğrulama
- **CSRF Protection**: Cross-site request forgery koruması
- **SQL Injection Protection**: ORM tabanlı güvenlik
- **File Upload Security**: Güvenli dosya yükleme

## 🚀 Hızlı Başlangıç

### Ön Gereksinimler

```bash
# Sistem gereksinimleri
Python 3.9+
PostgreSQL 12+
Git
```

### ⚡ Hızlı Kurulum

```bash
# 1. Projeyi klonlayın
git clone https://github.com/faikerkan/CallQualityHub.git
cd CallQualityHub

# 2. Virtual environment oluşturun
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Çevre değişkenlerini ayarlayın
cp .env-sample .env
# .env dosyasını düzenleyin

# 5. Veritabanını hazırlayın
python manage.py migrate
python manage.py createsuperuser

# 6. Sunucuyu başlatın
python manage.py runserver
```

🎉 **Tebrikler!** CallQualityHub artık http://127.0.0.1:8000 adresinde çalışıyor.

## ⚙️ Detaylı Kurulum

### 1. PostgreSQL Kurulumu

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS (Homebrew)
brew install postgresql

# Windows
# PostgreSQL'i resmi siteden indirin
```

### 2. Veritabanı Oluşturma

```sql
-- PostgreSQL shell'de çalıştırın
CREATE DATABASE qualityhub;
CREATE USER qualityhubuser WITH PASSWORD 'güçlü_şifre_buraya';
GRANT ALL PRIVILEGES ON DATABASE qualityhub TO qualityhubuser;
```

### 3. Çevre Değişkenleri (.env)

```env
# Django Ayarları
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# PostgreSQL Veritabanı
DB_NAME=qualityhub
DB_USER=qualityhubuser
DB_PASSWORD=güçlü_şifre_buraya
DB_HOST=localhost
DB_PORT=5432

# E-posta Ayarları (Opsiyonel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4. İlk Verileri Yükleme

```bash
# Örnek verileri yüklemek için
python manage.py loaddata fixtures/sample_data.json

# Veya manuel olarak admin panelinden kullanıcı ve form oluşturun
```

## 💻 Kullanım

### Kullanıcı Rolleri

#### 👑 **Admin (Yönetici)**
- Tüm sistem ayarlarına erişim
- Kullanıcı yönetimi
- Değerlendirme formları oluşturma
- Sistem raporları görüntüleme

#### 🔍 **Kalite Uzmanı**
- Çağrı kayıtları yükleme
- Değerlendirme yapma
- Kendi raporlarını görüntüleme

#### 👤 **Temsilci**
- Kendi değerlendirmelerini görüntüleme
- Performans raporlarına erişim

### Temel İşlem Akışı

1. **Çağrı Kaydı Yükleme**: Kalite uzmanı ses dosyasını sisteme yükler
2. **Değerlendirme Yapma**: Belirlenen kriterlere göre değerlendirme
3. **Rapor Oluşturma**: Otomatik olarak performans raporları oluşturulur
4. **Geribildirim**: Temsilci sonuçları görüntüler ve gelişim alanlarını belirler

## 🛠️ Geliştirme

### Proje Yapısı

```
CallQualityHub/
├── accounts/          # Kullanıcı yönetimi
├── calls/            # Çağrı kayıtları ve değerlendirmeler
├── dashboard/        # Dashboard ve raporlar
├── api/              # REST API endpoints
├── templates/        # HTML şablonlar
├── static/           # Statik dosyalar (CSS, JS, resimler)
├── media/            # Yüklenen dosyalar
├── docs/             # Proje dokümantasyonu
└── tests/            # Test dosyaları
```

### Test Çalıştırma

```bash
# Tüm testleri çalıştır
python manage.py test

# Specific app testleri
python manage.py test accounts
python manage.py test calls

# Coverage ile
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Kod Kalitesi

```bash
# Linting
pip install flake8
flake8 .

# Type checking
pip install mypy
mypy .

# Security check
pip install bandit
bandit -r .
```

## 📊 API Dokümantasyonu

### Authentication

```bash
# Token almak için
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### Endpoints

```bash
# Kullanıcılar
GET    /api/users/          # Kullanıcı listesi
POST   /api/users/          # Yeni kullanıcı
GET    /api/users/{id}/     # Kullanıcı detayı

# Çağrılar
GET    /api/calls/          # Çağrı listesi
POST   /api/calls/          # Yeni çağrı
GET    /api/calls/{id}/     # Çağrı detayı

# Değerlendirmeler
GET    /api/evaluations/    # Değerlendirme listesi
POST   /api/evaluations/    # Yeni değerlendirme
GET    /api/evaluations/{id}/  # Değerlendirme detayı
```

Detaylı API dokümantasyonu için: http://localhost:8000/api/docs/

## 🚀 Production Deployment

### Docker ile Deploy

```bash
# Docker image oluştur
docker build -t callqualityhub .

# Docker Compose ile çalıştır
docker-compose up -d
```

### Heroku Deploy

```bash
# Heroku CLI kurulumu sonrası
heroku create callqualityhub
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set DEBUG=False
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Manuel Server Kurulumu

```bash
# Gunicorn kurulumu
pip install gunicorn

# Static dosyaları topla
python manage.py collectstatic

# Gunicorn ile çalıştır
gunicorn call_quality_hub.wsgi:application --bind 0.0.0.0:8000
```

## 🔧 Konfigürasyon

### Performance Optimizasyonu

```python
# settings.py'de cache ayarları
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Güvenlik Ayarları

```python
# Production için önerilen ayarlar
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

## 🤝 Katkıda Bulunma

CallQualityHub'a katkıda bulunmak istiyorsanız:

1. **Fork** edin
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. **Commit** yapın (`git commit -m 'feat: add amazing feature'`)
4. **Push** edin (`git push origin feature/amazing-feature`)
5. **Pull Request** açın

Detaylı bilgi için [CONTRIBUTING.md](CONTRIBUTING.md) dosyasını okuyun.

### 🐛 Hata Bildirimi

Hata bulduysanız lütfen [issue açın](https://github.com/faikerkan/CallQualityHub/issues) ve şunları belirtin:

- Hatanın tanımı
- Adım adım nasıl tekrarlanacağı
- Beklenen davranış
- Ekran görüntüleri (varsa)
- Sistem bilgileri

## 📝 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

## 👥 Takım

- **Geliştirici**: [Faik Erkan Gürşen](https://github.com/faikerkan)
- **Design**: Modern Glassmorphism UI/UX
- **Backend**: Django REST Framework
- **Frontend**: TailwindCSS + Vanilla JS

## 🙏 Teşekkürler

Bu projeyi mümkün kılan harika açık kaynak projelerine teşekkürler:

- [Django](https://djangoproject.com/) - Web framework
- [TailwindCSS](https://tailwindcss.com/) - CSS framework
- [PostgreSQL](https://postgresql.org/) - Veritabanı
- [Django REST Framework](https://django-rest-framework.org/) - API

## 📞 İletişim

- **Email**: faikerkangursen@icloud.com
- **LinkedIn**: [Faik Erkan Gürşen](https://www.linkedin.com/in/faikerkan/)
- **GitHub**: [faikerkan](https://github.com/faikerkan)

---

<div align="center">

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**

Made with ❤️ by [Faik Erkan](https://github.com/faikerkan)

</div> 