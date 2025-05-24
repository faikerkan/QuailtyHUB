# 🤝 CallQualityHub'a Katkıda Bulunma Kılavuzu

CallQualityHub projesine katkıda bulunmak istediğiniz için teşekkür ederiz! Bu kılavuz, projeye nasıl katkıda bulunabileceğinizi açıklar.

## 📋 İçerik

- [Davranış Kuralları](#davranış-kuralları)
- [Nasıl Katkıda Bulunurum?](#nasıl-katkıda-bulunurum)
- [Hata Bildirimi](#hata-bildirimi)
- [Özellik İsteği](#özellik-isteği)
- [Kod Katkısı](#kod-katkısı)
- [Geliştirme Ortamı](#geliştirme-ortamı)
- [Kod Standartları](#kod-standartları)
- [Test Yazma](#test-yazma)
- [Pull Request Süreci](#pull-request-süreci)

## 📜 Davranış Kuralları

Bu proje ve topluluğu herkes için taciz içermeyen bir deneyim yaşatmayı taahhüt eder. Katılımcılardan:

- 🎯 Yapıcı ve saygılı olmaları
- 🌟 Farklı görüşlere açık olmaları  
- 🤝 Birbirlerine yardım etmeleri
- 📚 Öğrenme odaklı olmaları

## 🚀 Nasıl Katkıda Bulunurum?

Katkıda bulunmanın birçok yolu vardır:

### 📝 Dokümantasyon
- README'yi iyileştirme
- API dokümantasyonu yazma
- Eğitim materyalleri oluşturma
- Çeviri yapma

### 🐛 Hata Tespiti
- Hataları bulma ve raporlama
- Hata düzeltmeleri önerme
- Test senaryoları yazma

### 💡 Özellik Geliştirme
- Yeni özellikler önerme
- UI/UX iyileştirmeleri
- Performance optimizasyonları

### 🧪 Test
- Unit test yazma
- Integration test yazma
- Manual test yapma

## 🐛 Hata Bildirimi

Hata bulduğunuzda:

1. **Önce ara**: Aynı hata daha önce raporlanmış mı kontrol edin
2. **Issue oluştur**: [GitHub Issues](https://github.com/username/callqualityhub/issues) sayfasında yeni issue açın
3. **Detayları ekleyin**:
   - Hatanın açıklaması
   - Yeniden üretme adımları
   - Beklenen davranış
   - Ekran görüntüleri (varsa)
   - Sistem bilgileri (OS, tarayıcı, Python versiyonu)

### Hata Raporu Şablonu

```markdown
## Hata Açıklaması
[Hatanın kısa açıklaması]

## Yeniden Üretme Adımları
1. '...' sayfasına git
2. '...' butonuna tıkla
3. '...' formunu doldur
4. Hata görülür

## Beklenen Davranış
[Ne olması gerektiğini açıklayın]

## Ekran Görüntüleri
[Varsa ekran görüntülerini ekleyin]

## Ortam Bilgileri
- OS: [örn. macOS 12.0]
- Tarayıcı: [örn. Chrome 95.0]
- Python: [örn. 3.9.7]
- Django: [örn. 4.2.0]
```

## 💡 Özellik İsteği

Yeni özellik önerirken:

1. **Issue oluştur**: "Feature Request" etiketiyle
2. **Amacı açıkla**: Özelliğin neden gerekli olduğunu belirt
3. **Detayları ver**: Nasıl çalışması gerektiğini açıkla
4. **Alternatifler**: Düşündüğünüz alternatifleri paylaş

### Özellik İsteği Şablonu

```markdown
## Özellik Açıklaması
[Özelliğin kısa açıklaması]

## Problem
[Bu özellik hangi problemi çözecek?]

## Çözüm
[Önerilen çözümün detaylı açıklaması]

## Alternatifler
[Düşündüğünüz alternatif çözümler]

## Ek Bilgiler
[Eklemek istediğiniz diğer bilgiler]
```

## 💻 Kod Katkısı

### Geliştirme Ortamı Kurulumu

1. **Repository'yi fork edin**
2. **Clone edin**:
   ```bash
   git clone https://github.com/YOURUSERNAME/callqualityhub.git
   cd callqualityhub
   ```

3. **Geliştirme ortamını kurun**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Veritabanını kurun**:
   ```bash
   cp .env-sample .env
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Branch oluşturun**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📏 Kod Standartları

### Python Kod Stili

- **PEP 8** standartlarına uyun
- **Black** code formatter kullanın
- **isort** ile import sıralaması yapın
- **flake8** ile linting yapın

```bash
# Kod formatlama
black .
isort .

# Linting
flake8 .
```

### Django Konvansiyonları

- Model adları PascalCase (örn: `CallRecord`)
- View fonksiyonları snake_case (örn: `user_profile`)
- Template adları kebab-case (örn: `user-profile.html`)
- URL patterns snake_case (örn: `user_profile`)

### Frontend Standartları

- **TailwindCSS** class sıralaması
- **Semantic HTML** kullanın
- **Accessibility** standartlarına uyun
- **Mobile-first** responsive design

### Git Commit Mesajları

[Conventional Commits](https://www.conventionalcommits.org/) formatını kullanın:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Örnekler:**
```bash
feat(auth): add password reset functionality
fix(dashboard): resolve chart rendering issue
docs: update installation guide
style: format code with black
refactor(models): optimize database queries
test: add unit tests for user registration
```

**Türler:**
- `feat`: Yeni özellik
- `fix`: Hata düzeltme
- `docs`: Dokümantasyon
- `style`: Kod formatlama
- `refactor`: Kod yeniden düzenleme
- `test`: Test ekleme/düzeltme
- `chore`: Diğer değişiklikler

## 🧪 Test Yazma

### Test Türleri

1. **Unit Tests**: Tekil fonksiyonları test edin
2. **Integration Tests**: Bileşenlerin birlikte çalışmasını test edin
3. **Functional Tests**: Kullanıcı deneyimini test edin

### Test Yazma Kuralları

```python
# tests/test_models.py
import pytest
from django.test import TestCase
from accounts.models import CustomUser

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """Test that user is created correctly"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_str_representation(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), 'testuser')
```

### Test Çalıştırma

```bash
# Tüm testler
python manage.py test

# Belirli app testleri
python manage.py test accounts

# Coverage raporu
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 🔄 Pull Request Süreci

### PR Hazırlığı

1. **Tests yazın**: Yeni kod için testler ekleyin
2. **Testleri çalıştırın**: Tüm testlerin geçtiğinden emin olun
3. **Dokümantasyon**: Gerekirse dokümantasyonu güncelleyin
4. **Kod kalitesi**: Linting ve formatlama kontrolleri yapın

### PR Oluşturma

1. **Açıklayıcı başlık**: Ne yaptığınızı özetleyin
2. **Detaylı açıklama**: Değişiklikleri detaylandırın
3. **Test bilgileri**: Nasıl test edildiğini belirtin
4. **Ekran görüntüleri**: UI değişiklikleri varsa ekleyin

### PR Şablonu

```markdown
## Değişiklik Açıklaması
[Yaptığınız değişikliklerin kısa açıklaması]

## Değişiklik Türü
- [ ] Bug fix (breaking change olmayan hata düzeltme)
- [ ] New feature (breaking change olmayan yeni özellik)
- [ ] Breaking change (mevcut fonksiyonaliteyi etkileyen değişiklik)
- [ ] Documentation update (dokümantasyon güncellemesi)

## Test
- [ ] Testler yazıldı
- [ ] Mevcut testler geçiyor
- [ ] Manuel test yapıldı

## Checklist
- [ ] Kod PEP 8 standartlarına uygun
- [ ] Self-review yapıldı
- [ ] Dokümantasyon güncellendi
- [ ] Breaking change yok veya belgelenmiş
```

### Review Süreci

1. **Otomatik kontroller**: CI/CD pipeline kontrolleri geçmeli
2. **Kod review**: En az bir maintainer'dan onay alın
3. **Tartışma**: Geri bildirimler için hazır olun
4. **Güncelleme**: İstenen değişiklikleri yapın

## 🏷️ Issue ve PR Etiketleri

### Issue Etiketleri
- `bug`: Hata raporları
- `enhancement`: Yeni özellik istekleri
- `documentation`: Dokümantasyon işleri
- `good first issue`: Yeni başlayanlar için
- `help wanted`: Yardım gerekli
- `priority-high`: Yüksek öncelik
- `priority-low`: Düşük öncelik

### PR Etiketleri
- `WIP`: Work in Progress
- `ready-for-review`: Review için hazır
- `needs-testing`: Test gerekli
- `breaking-change`: Breaking change içeriyor

## 🤔 Sorular?

Herhangi bir sorunuz varsa:

1. **Issues**: GitHub Issues sayfasında soru sorabilirsiniz
2. **Discussions**: GitHub Discussions'da tartışma başlatabilirsiniz
3. **Email**: admin@callqualityhub.com

## 🙏 Teşekkürler

Katkılarınız projeyi daha iyi hale getiriyor. Her türlü katkı değerlidir ve takdir edilir!

---

**Happy Coding! 🚀** 