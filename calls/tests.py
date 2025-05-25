from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Call, CallEvaluation


class CallModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_call_creation(self):
        """Test that a call can be created successfully"""
        call = Call.objects.create(
            agent=self.user,
            customer_phone="1234567890",
            duration=300,
            call_type="inbound",
        )
        self.assertEqual(call.agent, self.user)
        self.assertEqual(call.customer_phone, "1234567890")
        self.assertEqual(call.duration, 300)
        self.assertEqual(call.call_type, "inbound")

    def test_call_str_method(self):
        """Test the string representation of Call model"""
        call = Call.objects.create(
            agent=self.user,
            customer_phone="1234567890",
            duration=300,
            call_type="inbound",
        )
        expected_str = f"Call {call.id} - {self.user.username}"
        self.assertEqual(str(call), expected_str)


class CallViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_call_list_view_requires_login(self):
        """Test that call list view requires authentication"""
        response = self.client.get(reverse("calls:call_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_call_list_view_authenticated(self):
        """Test call list view with authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("calls:call_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Çağrı Listesi")


class CallEvaluationTest(TestCase):
    def setUp(self):
        self.agent = User.objects.create_user(
            username="agent", email="agent@example.com", password="testpass123"
        )
        self.evaluator = User.objects.create_user(
            username="evaluator", email="evaluator@example.com", password="testpass123"
        )
        self.call = Call.objects.create(
            agent=self.agent,
            customer_phone="1234567890",
            duration=300,
            call_type="inbound",
        )

    def test_evaluation_creation(self):
        """Test that a call evaluation can be created"""
        evaluation = CallEvaluation.objects.create(
            call=self.call,
            evaluator=self.evaluator,
            score=85,
            notes="Good call handling",
        )
        self.assertEqual(evaluation.call, self.call)
        self.assertEqual(evaluation.evaluator, self.evaluator)
        self.assertEqual(evaluation.score, 85)
        self.assertEqual(evaluation.notes, "Good call handling")

    def test_evaluation_str_method(self):
        """Test the string representation of CallEvaluation model"""
        evaluation = CallEvaluation.objects.create(
            call=self.call,
            evaluator=self.evaluator,
            score=85,
            notes="Good call handling",
        )
        expected_str = f"Evaluation for Call {self.call.id} - Score: 85"
        self.assertEqual(str(evaluation), expected_str)
