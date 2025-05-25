from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class MainProjectTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_home_page_redirect(self):
        """Test that home page redirects to login for unauthenticated users"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_home_page_authenticated(self):
        """Test home page access for authenticated users"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)  # Redirects to dashboard

    def test_dashboard_access(self):
        """Test dashboard access requires authentication"""
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_authenticated(self):
        """Test dashboard access for authenticated users"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")


class SettingsTest(TestCase):
    """Test Django settings configuration"""

    def test_debug_setting(self):
        """Test that DEBUG setting is properly configured"""
        from django.conf import settings

        # In test environment, DEBUG should be True or False based on configuration
        self.assertIsInstance(settings.DEBUG, bool)

    def test_installed_apps(self):
        """Test that required apps are installed"""
        from django.conf import settings

        required_apps = [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "users",
            "calls",
        ]
        for app in required_apps:
            self.assertIn(app, settings.INSTALLED_APPS)

    def test_database_configuration(self):
        """Test that database is properly configured"""
        from django.conf import settings

        self.assertIn("default", settings.DATABASES)
        self.assertIn("ENGINE", settings.DATABASES["default"])
