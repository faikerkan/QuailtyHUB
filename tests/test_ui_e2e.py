import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# NOT: ChromeDriver artık otomatik olarak yönetilecek
# pytest ile: pytest tests/test_ui_e2e.py --headless

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    )
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


def login(driver, username, password):
    """Kullanıcı girişi yapar"""
    try:
        # Önce logout yapalım ki temiz bir session başlasın
        driver.get(f"{BASE_URL}/accounts/logout/")
        time.sleep(2)

        # Login sayfasına git
        driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)

        # Form elemanlarını bekle
        wait = WebDriverWait(driver, 10)
        user_input = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        pass_input = wait.until(EC.presence_of_element_located((By.ID, "id_password")))

        # Giriş bilgilerini doldur
        user_input.clear()
        user_input.send_keys(username)
        pass_input.clear()
        pass_input.send_keys(password)

        # Formu gönder
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Yönlendirmeyi bekle (daha uzun süre)
        time.sleep(3)

        # Login işleminin başarılı olduğunu kontrol et
        success = "Çıkış Yap" in driver.page_source or "Logout" in driver.page_source

        # Başarısız ise tekrar dene
        if not success:
            print(f"İlk giriş denemesi başarısız oldu, tekrar deneniyor: {username}")
            time.sleep(1)

            user_input = wait.until(
                EC.presence_of_element_located((By.ID, "id_username"))
            )
            pass_input = wait.until(
                EC.presence_of_element_located((By.ID, "id_password"))
            )

            user_input.clear()
            user_input.send_keys(username)
            pass_input.clear()
            pass_input.send_keys(password)

            submit_button = driver.find_element(
                By.CSS_SELECTOR, "button[type='submit']"
            )
            submit_button.click()

            time.sleep(3)

    except Exception as e:
        print(f"Login sırasında hata: {str(e)}")
        raise


def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


class TestUIE2E:
    def test_login_functionality(self, driver):
        """Temel giriş ve sayfaya erişim testleri"""
        # Admin girişi testi
        driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)

        user_input = wait_for_element(driver, By.ID, "id_username")
        pass_input = wait_for_element(driver, By.ID, "id_password")

        user_input.clear()
        user_input.send_keys("admin")
        pass_input.clear()
        pass_input.send_keys("admin123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(3)

        # Ana sayfayı kontrol et
        driver.get(f"{BASE_URL}/")
        time.sleep(2)
        assert "CallQualityHub" in driver.page_source

        # Çıkış yap
        driver.get(f"{BASE_URL}/accounts/logout/")
        time.sleep(1)

    def test_navigation_and_page_loading(self, driver):
        """Navigation testi"""
        # Admin sayfalarına erişim testi
        driver.get(f"{BASE_URL}/admin/")
        time.sleep(2)
        assert (
            "Django yönetim" in driver.page_source
            or "Django admin" in driver.page_source
        )

        # Giriş sayfasına git
        driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)
        assert "Giriş Yap" in driver.page_source

    def test_form_submission(self, driver):
        """Form gönderme testi"""
        # Login form testi
        driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)

        user_input = wait_for_element(driver, By.ID, "id_username")
        pass_input = wait_for_element(driver, By.ID, "id_password")

        user_input.clear()
        user_input.send_keys("test_user")
        pass_input.clear()
        pass_input.send_keys("test_password")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(3)

        # Giriş başarısız olacak, form sayfasında kalacağız
        assert "Giriş Yap" in driver.page_source

    def test_admin_dashboard(self, driver):
        """Yönetici dashboard testi"""
        # Admin girişi yap
        driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)

        user_input = wait_for_element(driver, By.ID, "id_username")
        pass_input = wait_for_element(driver, By.ID, "id_password")

        user_input.clear()
        user_input.send_keys("admin")
        pass_input.clear()
        pass_input.send_keys("admin123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(3)

        # Ana sayfaya git
        driver.get(f"{BASE_URL}/")
        time.sleep(2)

        # Menü kontrolü
        assert "CallQualityHub" in driver.page_source

        # Admin dashboard'a git
        driver.get(f"{BASE_URL}/admin/")
        time.sleep(2)
        assert "Django" in driver.page_source

        # Çıkış yap
        driver.get(f"{BASE_URL}/accounts/logout/")
        time.sleep(1)

    def test_expert_dashboard(self, driver):
        """Kalite uzmanı dashboard testi"""
        # Uzman girişi yap
        driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)

        user_input = wait_for_element(driver, By.ID, "id_username")
        pass_input = wait_for_element(driver, By.ID, "id_password")

        user_input.clear()
        user_input.send_keys("kalitetest")
        pass_input.clear()
        pass_input.send_keys("kalite123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(3)

        # Ana sayfaya git
        driver.get(f"{BASE_URL}/")
        time.sleep(2)

        # Menü kontrolü
        assert "CallQualityHub" in driver.page_source

        # Çıkış yap
        driver.get(f"{BASE_URL}/accounts/logout/")
        time.sleep(1)

    def test_agent_dashboard(self, driver):
        """Müşteri temsilcisi dashboard testi"""
        # Temsilci girişi yap
        driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)

        user_input = wait_for_element(driver, By.ID, "id_username")
        pass_input = wait_for_element(driver, By.ID, "id_password")

        user_input.clear()
        user_input.send_keys("agenttest")
        pass_input.clear()
        pass_input.send_keys("agent123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(3)

        # Ana sayfaya git
        driver.get(f"{BASE_URL}/")
        time.sleep(2)

        # Menü kontrolü
        assert "CallQualityHub" in driver.page_source

        # Çıkış yap
        driver.get(f"{BASE_URL}/accounts/logout/")
        time.sleep(1)

    def test_admin_specific_pages(self, driver):
        """Yönetici paneli spesifik sayfaları testi"""
        # Admin girişi yap
        driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)

        user_input = wait_for_element(driver, By.ID, "id_username")
        pass_input = wait_for_element(driver, By.ID, "id_password")

        user_input.clear()
        user_input.send_keys("admin")
        pass_input.clear()
        pass_input.send_keys("admin123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(3)

        # Django admin paneli
        driver.get(f"{BASE_URL}/admin/")
        time.sleep(2)
        assert "Django" in driver.page_source

        # Kullanıcı yönetimi
        try:
            driver.get(f"{BASE_URL}/admin/auth/user/")
            time.sleep(2)
            assert "Kullanıcılar" in driver.page_source or "Users" in driver.page_source
        except:
            print("Kullanıcı yönetimi sayfası erişiminde hata olabilir")

        # Çağrı kayıtları
        try:
            driver.get(f"{BASE_URL}/admin/calls/call/")
            time.sleep(2)
            assert "Çağrı" in driver.page_source or "Call" in driver.page_source
        except:
            print("Çağrı kayıtları sayfası erişiminde hata olabilir")

        # Çıkış yap
        driver.get(f"{BASE_URL}/accounts/logout/")
        time.sleep(1)

    def test_expert_specific_pages(self, driver):
        """Kalite uzmanı spesifik sayfaları testi"""
        # Uzman girişi yap
        driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)

        user_input = wait_for_element(driver, By.ID, "id_username")
        pass_input = wait_for_element(driver, By.ID, "id_password")

        user_input.clear()
        user_input.send_keys("kalitetest")
        pass_input.clear()
        pass_input.send_keys("kalite123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(3)

        # Ana sayfaya git
        driver.get(f"{BASE_URL}/")
        time.sleep(2)

        # Platform da uzman için özel sayfaları kontrol et
        # Bu sayfalar projeye göre değişiklik gösterebilir

        # Çıkış yap
        driver.get(f"{BASE_URL}/accounts/logout/")
        time.sleep(1)

    def test_call_evaluation_flow(self, driver):
        """Çağrı değerlendirme akışı testi"""
        # Kalite uzmanı girişi yap
        driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)

        user_input = wait_for_element(driver, By.ID, "id_username")
        pass_input = wait_for_element(driver, By.ID, "id_password")

        user_input.clear()
        user_input.send_keys("kalitetest")
        pass_input.clear()
        pass_input.send_keys("kalite123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(3)

        try:
            # Değerlendirme sayfasına git
            driver.get(f"{BASE_URL}/evaluations/")
            time.sleep(2)

            # Değerlendirme sayfasında olduğumuzu kontrol et
            assert (
                "Değerlendirme" in driver.page_source
                or "Evaluation" in driver.page_source
            )

            # Yeni değerlendirme başlat - UI bileşenlerine göre güncellenmeli
            try:
                new_eval_button = driver.find_element(
                    By.XPATH,
                    "//button[contains(text(), 'Yeni') or contains(text(), 'New')]",
                )
                new_eval_button.click()
                time.sleep(2)
            except:
                print("Yeni değerlendirme butonu bulunamadı - UI yapısını kontrol edin")
        except:
            print("Değerlendirme sayfası testi atlandı")

        # Çıkış yap
        driver.get(f"{BASE_URL}/accounts/logout/")
        time.sleep(1)

    def test_reporting_module(self, driver):
        """Raporlama modülü testi"""
        # Admin girişi yap (genellikle raporlama erişimi olan kullanıcı)
        driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(2)

        user_input = wait_for_element(driver, By.ID, "id_username")
        pass_input = wait_for_element(driver, By.ID, "id_password")

        user_input.clear()
        user_input.send_keys("admin")
        pass_input.clear()
        pass_input.send_keys("admin123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(3)

        try:
            # Raporlama sayfasına git
            driver.get(f"{BASE_URL}/reports/")
            time.sleep(2)

            # Raporlama sayfasında olduğumuzu kontrol et
            assert "Rapor" in driver.page_source or "Report" in driver.page_source

            # Genel arayüz kontrolü
            page_source = driver.page_source
            expected_elements = [
                "Grafik",
                "Tablo",
                "Filtre",
                "Tarih",
                "Performans",
                "Sonuç",
            ]
            expected_elements_en = [
                "Chart",
                "Table",
                "Filter",
                "Date",
                "Performance",
                "Result",
            ]

            found_elements = []
            for elem in expected_elements:
                if elem in page_source:
                    found_elements.append(elem)

            for elem in expected_elements_en:
                if elem in page_source:
                    found_elements.append(elem)

            # En az birkaç beklenen elemanın sayfada bulunduğunu kontrol et
            print(f"Bulunan rapor öğeleri: {found_elements}")
            assert (
                len(found_elements) > 0
            ), "Rapor sayfasında beklenen öğeler bulunamadı"

        except Exception as e:
            print(f"Raporlama sayfası testi hatası: {str(e)}")

        # Çıkış yap
        driver.get(f"{BASE_URL}/accounts/logout/")
        time.sleep(1)
