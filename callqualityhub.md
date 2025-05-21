# CallQualityHub - Proje Planı ve Uygulama Rehberi

## 🎯 Proje Amacı

Çağrı merkezi operasyonlarında kalite değerlendirme süreçlerini web tabanlı ve dinamik şekilde yönetmek, kolaylaştırmak ve raporlamak için geliştirilmiştir.

## 📌 Kullanılan Teknolojiler

* **Backend:** Django (Python)
* **Frontend:** Django Templates & TailwindCSS
* **Veritabanı:** PostgreSQL
* **Depolama:** Dosya Sistemi
* **Yetkilendirme:** Django Session Authentication
* **API:** Django REST Framework (DRF)

## 🔐 Kullanıcı Rolleri ve Yetkileri

| Rol                    | Yetkiler / İşlevler                                                      |
| ---------------------- | ------------------------------------------------------------------------ |
| **Yönetici**           | Kullanıcı yönetimi, form ve puanlama yönetimi, raporlama ve dashboardlar |
| **Kalite Uzmanı**      | Çağrı değerlendirme oluşturma ve düzenleme, kişisel dashboard            |
| **Müşteri Temsilcisi** | Değerlendirme sonuçlarını görüntüleme, kişisel dashboard                 |

## 📁 Proje Dizini Yapısı

```
call_quality_hub/
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/accounts/
├── calls/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/calls/
├── dashboard/
│   ├── views.py
│   ├── urls.py
│   └── templates/dashboard/
├── api/
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── static/
│   ├── css/
│   └── js/
├── media/
│   └── call_records/
├── templates/
│   └── base.html
├── requirements.txt
└── manage.py
```

## 📐 Modeller (Django ORM)

### Kullanıcı Modeli (accounts/models.py)

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Yönetici'),
        ('expert', 'Kalite Uzmanı'),
        ('agent', 'Müşteri Temsilcisi'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
```

### Çağrı ve Değerlendirme Modelleri (calls/models.py)

```python
class EvaluationForm(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    fields = models.JSONField()

class CallRecord(models.Model):
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    agent = models.ForeignKey(CustomUser, related_name="calls", on_delete=models.SET_NULL, null=True)
    audio_file = models.FileField(upload_to='call_records/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Evaluation(models.Model):
    call = models.ForeignKey(CallRecord, on_delete=models.CASCADE)
    evaluator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    form = models.ForeignKey(EvaluationForm, on_delete=models.SET_NULL, null=True)
    scores = models.JSONField()
    final_note = models.TextField(blank=True, null=True)
    evaluated_at = models.DateTimeField(auto_now_add=True)
```

## 📊 Dashboardlar

### Yönetici Dashboard

* Kullanıcı Yönetimi (CRUD)
* Form Özelleştirme ve Yönetimi
* Çağrı ve Değerlendirme Raporları (Günlük, Haftalık, MT bazlı)

### Kalite Uzmanı Dashboard

* Değerlendirilecek Çağrılar Listesi
* Yapılan Değerlendirmeler
* Performans İstatistikleri

### Müşteri Temsilcisi Dashboard

* Değerlendirilmiş Çağrılar
* Performans Özeti

## 🚀 API Yapısı (DRF)

* **GET** `/api/calls/` - Çağrıları listele
* **POST** `/api/calls/upload/` - Çağrı yükle
* **GET** `/api/evaluations/{id}/` - Değerlendirme detayı
* **POST** `/api/evaluations/create/` - Değerlendirme oluştur
* **GET** `/api/users/` - Kullanıcıları listele

## 🧪 Test ve CI/CD

* Django Unit Testleri
* Django REST Framework API Testleri
* Selenium/Cypress E2E Testleri
* GitHub Actions CI/CD pipeline

## 📈 Raporlama Özellikleri

* Ortalama Çağrı Puanları
* MT Performans Raporları
* Kalite Uzmanı Performans Raporları
* Aylık, Haftalık ve operasyon bazlı raporlar

## 📌 Geliştirme Adımları

1. Django projesini oluştur ve ayarlarını yap
2. Kullanıcı yetkilendirme ve profil yönetimini geliştir
3. Çağrı ve değerlendirme modellerini oluştur
4. Dinamik form yapısını geliştir
5. Dashboardları ve görsel arayüzleri oluştur
6. API uç noktalarını oluştur
7. Testleri yaz ve CI/CD pipeline kur
8. Sistemi deploy et ve ilk kullanıcı testlerini başlat

## 🔗 Ek Notlar

* MP3 dosyaları için medya dizini kullan
* Ölçeklendirme için cloud entegrasyonu (AWS S3 vb.) gelecekte düşünülmeli

Bir çağrı merkezi değerlendirme programı yazmak istiyorum. Bunun mimarisi, testleri ve yapılarıyla birlikte bir proje haline gelmesini istiyorum. Bu bir çağrı merkezi kalite değerlendirme programı olacak ve her operasyonun ihtiyaçlarına göre özelleştirilebilir olacak.

Kullanıcı rolleri:

Yönetici: Kullanıcı oluşturma, silme ve yetki değiştirme işlemlerini yapabilecek. Aynı zamanda "kalite değerlendirme formu"nu özelleştirebilecek ve değiştirebilecek. Puan içeriğini yönetebilecek. Aynı zamanda çağrı kayıtlarının içeride tutulabilmesi için çağrı kuyruğu kısımlarını da özelleştirebilecek

Kalite Uzmanı: Kalite değerlendirme uzmanı, çağrı değerlendirmesi yapabilecek. Değerlendirme yapabildiği gibi kendi değerlendirmelerini revize edebilecek, editleyebilecek ancak silemeyecek.

Müşteri Temsilcisi: Müşteri temsilcisi çağrıları değerlendirilen kişidir. Kendi ekranında değerlendirilen çağrılarını görebilecek, içeriğini değiştiremeden puanlamaları ve yazılanları görebilecek.

web tabanlı bir uygulama olacak. Django uygun olacaktır diye düşünüyorum. Kullanıcı yetkilendirmesiyle ilgili kısımda bir fikrim yok. En kullanıcı dostu olanı nasılsa öyle yapalım. Loglama için özel isteklerim yok. Formlar puan tabanlı olacak. Açık uçlu son bir "değerlendirme notu" olacak. Formlar farklı operasyonlara göre dinamik olarak özelleştirilebilir olacak. Çağrı kayıtları mp3 olarak tutulacak. Eğer mp3 olarak verilmediyse bile mp3 formasına çevirip kaydedecek. Çağrılar sisteme değerlendirme aşamasında kaydedilecek. Değerlendirme formunun içerisinde "ses yükle" isimli bir yer olacak. Kalite formuyla birlikte ilişkilendirilerek kaydedilecek. Yönetici için detaylı bir dashboard ekranı olarak. Hemen her kırılımda (ihtiyaçları ön gör) raporlama olacak.Kalite Uzmanlarının kendi değerlendirdikleri alan için ayrı bir dashboard olacak. özetle yönetici, kalite uzmanı ve müşteri temsilcisinin ayrı dashboard'arı olacak. Müşteri temsilcisi ise kendisine ait değerlendirilmiş çağrıları görecekler.Bildirime gereksinim şu aşamada yok. Testler tarafında gereksinimleri ve gerçek dünyaya uygunluk açısından sen kurgula. Günlük 100 değerlendirme ve min 50 kullanıcı iyi bir öngörü. Daha büyük operasyonlarda da kullanılabilir. Bu aşamada entegrasyona gerek yok ancak geliştiriciler için API yapısı kurulmalı. Veriler sonsuza dek saklanabilmeli.

## 🧪 Demo/Test Verisi ve Uçtan Uca Test Akışı

### 1. Örnek Kullanıcılar
- Yönetici: admin / admin123
- Kalite Uzmanı: kalitetest / kalite123
- Müşteri Temsilcisi: agenttest / agent123

### 2. Örnek Çağrı Kuyruğu
- Satış
- Destek

### 3. Örnek Değerlendirme Formu
- Adı: Standart Değerlendirme
- Alanlar:
  - greeting: Selamlama (type: number, max_score: 10)
  - problem_solving: Çözüm Üretme (type: number, max_score: 20)

### 4. Örnek Çağrı Kayıtları
- agent: agenttest
- call_queue: Satış
- phone_number: 5551234567
- audio_file: test.mp3
- call_date: 2024-06-01T11:00:00Z

### 5. Uçtan Uca Test Senaryosu
1. Yönetici ile giriş yap, kalite uzmanı ve agent kullanıcılarını oluştur.
2. Bir çağrı kuyruğu ve bir değerlendirme formu oluştur.
3. Kalite uzmanı ile giriş yap, yeni bir çağrı kaydı yükle.
4. Yüklenen çağrıya değerlendirme ekle (ör: Selamlama: 8, Çözüm Üretme: 18, Not: "Başarılı iletişim").
5. Agent ile giriş yapıp, kendi çağrılarını ve değerlendirmelerini görüntüle.
6. Yönetici ile tüm çağrı ve değerlendirmeleri kontrol et.

### 6. Test İçin Fixture veya Script
- (İsteğe bağlı) `manage.py loaddata` ile kullanılacak bir fixture dosyası hazırlanabilir.
- Alternatif olarak admin paneli üzerinden yukarıdaki adımlar manuel olarak uygulanabilir.
