#!/bin/bash

# Bu betik, SQLite'dan PostgreSQL'e veri aktarımı yapar
# Kullanım: ./transfer_data_to_postgres.sh

set -e  # Herhangi bir hata olduğunda betiği durdur

echo "CallQualityHub - SQLite'dan PostgreSQL'e Veri Aktarımı"
echo "======================================================"

# Geçerli dizin kontrolü
if [ ! -f "manage.py" ]; then
    echo "Hata: Bu betik Django projesinin kök dizininde çalıştırılmalıdır."
    exit 1
fi

# PostgreSQL bağlantısı için .env dosyasını kontrol et
if [ ! -f ".env" ]; then
    echo "Hata: .env dosyası bulunamadı. Önce .env-sample dosyasını kopyalayın."
    exit 1
fi

# Verileri dışa aktar
echo "[1/4] SQLite veritabanından verileri dışa aktarıyorum..."
python manage.py dumpdata --exclude auth.permission --exclude contenttypes --exclude admin.logentry --indent 2 > data.json

# settings.py'deki veritabanı yapılandırmasını kontrol et
echo "[2/4] PostgreSQL veritabanı yapılandırmasını kontrol ediyorum..."
if grep -q "django.db.backends.postgresql" call_quality_hub/settings.py; then
    echo "  - PostgreSQL yapılandırması settings.py dosyasında bulundu."
else
    echo "Hata: settings.py dosyasında PostgreSQL yapılandırması bulunamadı."
    echo "Lütfen önce settings.py dosyasını düzenleyin."
    exit 1
fi

# Migrasyonları uygula
echo "[3/4] PostgreSQL veritabanında migrasyonları uyguluyorum..."
python manage.py migrate

# Verileri içe aktar
echo "[4/4] Verileri PostgreSQL veritabanına aktarıyorum..."
python manage.py loaddata data.json

echo "======================================================"
echo "Veri aktarımı tamamlandı!"
echo "Yedek veri dosyası: data.json"
echo ""
echo "Önemli: Test amacıyla bir kullanıcı ile giriş yapmayı deneyin."
echo "Sorun yaşarsanız, SQLite'a geri dönmek için settings.py dosyasını düzenleyin." 