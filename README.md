# CallQualityHub - Çağrı Merkezi Kalite Değerlendirme Sistemi

CallQualityHub, çağrı merkezi operasyonlarında kalite değerlendirme süreçlerini web tabanlı ve dinamik şekilde yönetmek, kolaylaştırmak ve raporlamak için geliştirilmiş bir uygulamadır.

## 🚀 Özellikler

- Dinamik değerlendirme formları
- Rol tabanlı kullanıcı yetkilendirme (Yönetici, Kalite Uzmanı, Müşteri Temsilcisi)
- Çağrı kayıtlarının yüklenmesi ve saklanması
- Özelleştirilebilir puanlama sistemi
- Detaylı raporlama ve grafikler
- Kullanıcı dostu arayüz (TailwindCSS ile)
- RESTful API

## 🔧 Teknolojiler

- **Backend:** Django 4.2
- **Frontend:** Django Templates & TailwindCSS
- **Veritabanı:** PostgreSQL
- **API:** Django REST Framework
- **Dosya Yönetimi:** Django FileField

## 📋 Kurulum

### Ön Gereksinimler

- Python 3.8+
- PostgreSQL
- pip
- Node.js ve npm (TailwindCSS için)

### Adımlar

1. Repository'yi klonlayın:
   ```bash
   git clone https://github.com/username/callqualityhub.git
   cd callqualityhub
   ```

2. Sanal ortam oluşturun ve aktif edin:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac için
   venv\Scripts\activate  # Windows için
   ```

3. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. .env dosyasını yapılandırın (örnek .env.example dosyasını kopyalayarak):
   ```bash
   cp .env-sample .env
   ```

5. PostgreSQL veritabanını oluşturun:
   ```bash
   # PostgreSQL'e bağlanın
   sudo -u postgres psql
   
   # Veritabanı ve kullanıcı oluşturun
   CREATE DATABASE qualityhub;
   CREATE USER qualityhubuser WITH PASSWORD 'qualityhub123';
   ALTER ROLE qualityhubuser SET client_encoding TO 'utf8';
   ALTER ROLE qualityhubuser SET default_transaction_isolation TO 'read committed';
   ALTER ROLE qualityhubuser SET timezone TO 'Europe/Istanbul';
   GRANT ALL PRIVILEGES ON DATABASE qualityhub TO qualityhubuser;
   
   # PostgreSQL konsolundan çıkın
   \q
   ```

6. Django migrasyonlarını uygulayın:
   ```bash
   python manage.py migrate
   ```

7. TailwindCSS bağımlılıklarını yükleyin:
   ```bash
   python manage.py tailwind install
   ```

8. TailwindCSS geliştirme sunucusunu başlatın:
   ```bash
   python manage.py tailwind start
   ```

9. Geliştirme sunucusunu başlatın:
   ```bash
   python manage.py runserver
   ```

## 📚 Kullanım

### Yönetici Kullanıcısı Oluşturma

```bash
python manage.py createsuperuser
```

### Erişim Bilgileri

- **Yönetici Paneli:** `http://localhost:8000/admin/`
- **Uygulama:** `http://localhost:8000/`

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

## 📞 İletişim

Proje Yöneticisi - [admin@callqualityhub.com](mailto:admin@callqualityhub.com)

Proje Linki: [https://github.com/username/callqualityhub](https://github.com/username/callqualityhub)

## 🧪 Testler

Tümleşik testler için kök dizinde `tests/` klasörü bulunmaktadır. Testleri çalıştırmak için:

```bash
pytest
```

veya Django testleri için:

```bash
python manage.py test
```

Testler, uçtan uca senaryoları ve API fonksiyonlarını kapsamaktadır.

## 🚀 Canlı Ortama Dağıtım

Projeyi canlı ortama (üretime) dağıtmak için aşağıdaki adımları takip edebilirsiniz:

### 1. Sunucu Hazırlığı

```bash
# Gerekli paketlerin sunucuya kurulumu
sudo apt update
sudo apt install python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx

# Proje dizini oluşturma
sudo mkdir -p /var/www/callqualityhub
sudo chown -R $USER:$USER /var/www/callqualityhub
```

### 2. Veritabanı Kurulumu

```bash
# PostgreSQL'e bağlanın
sudo -u postgres psql

# Veritabanı ve kullanıcı oluşturun
CREATE DATABASE qualityhub;
CREATE USER qualityhubuser WITH PASSWORD 'guvenli_sifre';
ALTER ROLE qualityhubuser SET client_encoding TO 'utf8';
ALTER ROLE qualityhubuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE qualityhubuser SET timezone TO 'Europe/Istanbul';
GRANT ALL PRIVILEGES ON DATABASE qualityhub TO qualityhubuser;

# PostgreSQL konsolundan çıkın
\q
```

### 3. Proje Dağıtımı

```bash
# Proje kodlarını klonlayın
git clone https://github.com/username/callqualityhub.git /var/www/callqualityhub

# Sanal ortam oluşturun
cd /var/www/callqualityhub
python3 -m venv env
source env/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# .env dosyasını oluşturun
nano .env
# .env dosyasına canlı ortam ayarlarını ekleyin
```

### 4. Statik Dosyaları Toplayın ve Veritabanı Migrasyonlarını Çalıştırın

```bash
python manage.py collectstatic --no-input
python manage.py migrate
```

### 5. Gunicorn ve Nginx Yapılandırması

Detaylı yapılandırma adımları için `postgresql_canli_gecis_plani.md` dosyasına başvurun.

### 6. SSL Sertifikası Alın

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d alan_adiniz.com -d www.alan_adiniz.com
```

## 🔄 SQLite'dan PostgreSQL'e Veri Taşıma

Mevcut SQLite veritabanınızdaki verileri PostgreSQL'e taşımak için:

```bash
# 1. SQLite'dan veri dışa aktarma
python manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > data.json

# 2. PostgreSQL yapılandırmasına geçiş (settings.py değişikliği)
# 3. Veritabanını oluştur ve migrasyonları çalıştır
python manage.py migrate

# 4. Dışa aktarılan verileri PostgreSQL'e aktar
python manage.py loaddata data.json
```

## 📊 Yedekleme Stratejisi

Canlı ortamda düzenli yedekleme için:

```bash
# PostgreSQL veritabanı yedeği
pg_dump -U qualityhubuser -h localhost qualityhub > backup_$(date +%Y%m%d).sql

# Medya dosyaları yedeği
tar -czvf media_backup_$(date +%Y%m%d).tar.gz /var/www/callqualityhub/media
```

Otomatik yedekleme betikleri hakkında daha fazla bilgi için `postgresql_canli_gecis_plani.md` dosyasına başvurun. 