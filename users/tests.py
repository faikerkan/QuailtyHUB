from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import UserProfile


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_user_profile_creation(self):
        """Test that a user profile is created automatically"""
        # UserProfile should be created automatically via signal
        self.assertTrue(hasattr(self.user, "userprofile"))
        profile = self.user.userprofile
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.role, "agent")  # Default role

    def test_user_profile_str_method(self):
        """Test the string representation of UserProfile model"""
        profile = self.user.userprofile
        expected_str = f"{self.user.username} - {profile.role}"
        self.assertEqual(str(profile), expected_str)


class UserViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123",
            is_staff=True,
            is_superuser=True,
        )
        self.admin_user.userprofile.role = "admin"
        self.admin_user.userprofile.save()

        self.regular_user = User.objects.create_user(
            username="user", email="user@example.com", password="testpass123"
        )

    def test_user_list_view_requires_login(self):
        """Test that user list view requires authentication"""
        response = self.client.get(reverse("user_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_user_list_view_admin_access(self):
        """Test user list view with admin user"""
        self.client.login(username="admin", password="testpass123")
        response = self.client.get(reverse("user_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kullanıcı Listesi")

    def test_login_view(self):
        """Test login view"""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_user_login_success(self):
        """Test successful user login"""
        response = self.client.post(
            reverse("login"), {"username": "user", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_user_login_failure(self):
        """Test failed user login"""
        response = self.client.post(
            reverse("login"), {"username": "user", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 200)  # Stay on login page


class UserRoleTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin", email="admin@example.com", password="testpass123"
        )
        self.admin_user.userprofile.role = "admin"
        self.admin_user.userprofile.save()

        self.quality_expert = User.objects.create_user(
            username="expert", email="expert@example.com", password="testpass123"
        )
        self.quality_expert.userprofile.role = "quality_expert"
        self.quality_expert.userprofile.save()

        self.agent = User.objects.create_user(
            username="agent", email="agent@example.com", password="testpass123"
        )
        # Agent role is default

    def test_user_roles(self):
        """Test different user roles"""
        self.assertEqual(self.admin_user.userprofile.role, "admin")
        self.assertEqual(self.quality_expert.userprofile.role, "quality_expert")
        self.assertEqual(self.agent.userprofile.role, "agent")

    def test_role_choices(self):
        """Test that role choices are valid"""
        valid_roles = ["admin", "quality_expert", "agent"]
        for role in valid_roles:
            user = User.objects.create_user(
                username=f"test_{role}",
                email=f"{role}@example.com",
                password="testpass123",
            )
            user.userprofile.role = role
            user.userprofile.save()
            self.assertEqual(user.userprofile.role, role)
