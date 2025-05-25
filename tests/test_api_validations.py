import datetime
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from accounts.models import CustomUser
from calls.models import CallQueue, CallRecord, Evaluation, EvaluationForm


@pytest.mark.django_db
class TestAPIValidations:
    @pytest.fixture
    def setup_users(self):
        self.admin = CustomUser.objects.create_user(
            username="admin",
            password="admin123",
            role="admin",
            is_superuser=True,
            is_staff=True,
        )
        self.expert = CustomUser.objects.create_user(
            username="kalitetest", password="kalite123", role="expert"
        )
        self.agent = CustomUser.objects.create_user(
            username="agenttest", password="agent123", role="agent"
        )
        self.queue = CallQueue.objects.create(name="Test Queue")
        self.client = APIClient()
        return self.admin, self.expert, self.agent, self.queue

    @pytest.fixture
    def setup_form(self, setup_users):
        self.client.force_authenticate(user=self.admin)
        form_data = {
            "name": "Test Form",
            "fields": [
                {"key": "test1", "label": "Test 1", "type": "number", "max_score": 10},
                {"key": "test2", "label": "Test 2", "type": "number", "max_score": 10},
            ],
        }
        response = self.client.post("/api/evaluation-forms/", form_data, format="json")
        return response.data["id"]

    def test_unauthorized_access(self, setup_users):
        """Yetkisiz erişim testleri"""
        # Giriş yapmadan erişim denemeleri
        endpoints = ["/api/calls/", "/api/evaluation-forms/", "/api/evaluations/"]

        for endpoint in endpoints:
            response = self.client.get(endpoint)
            assert response.status_code in [401, 403]

    def test_agent_permissions(self, setup_users, setup_form):
        """Agent yetki sınırlamaları testleri"""
        self.client.force_authenticate(user=self.agent)

        # Agent'ın form oluşturma denemesi
        form_data = {
            "name": "Agent Form",
            "fields": [
                {"key": "test", "label": "Test", "type": "number", "max_score": 10}
            ],
        }
        response = self.client.post("/api/evaluation-forms/", form_data, format="json")
        assert response.status_code in [403, 405]

        # Agent'ın değerlendirme oluşturma denemesi
        eval_data = {
            "call": 1,
            "form": setup_form,
            "scores": {"test1": 8},
            "final_note": "Test note",
        }
        response = self.client.post("/api/evaluations/", eval_data, format="json")
        assert response.status_code in [400, 403, 405]

    def test_invalid_form_data(self, setup_users):
        """Form validasyon testleri"""
        self.client.force_authenticate(user=self.admin)

        # Boş form alanları
        response = self.client.post("/api/evaluation-forms/", {}, format="json")
        assert response.status_code == 400

        # Eksik alan bilgileri
        invalid_form = {
            "name": "Invalid Form",
            "fields": [{"key": "test"}],  # Eksik zorunlu alanlar
        }
        response = self.client.post(
            "/api/evaluation-forms/", invalid_form, format="json"
        )
        assert response.status_code == 400

    def test_call_upload_validations(self, setup_users):
        """Çağrı yükleme validasyonları"""
        self.client.force_authenticate(user=self.expert)

        # Boş dosya ile yükleme denemesi
        call_data = {
            "agent": self.agent.id,
            "call_queue": self.queue.id,
            "phone_number": "5551234567",
            "call_date": datetime.datetime.now().isoformat(),
        }
        response = self.client.post("/api/calls/upload/", call_data, format="multipart")
        assert response.status_code == 400

        # Geçersiz dosya formatı
        invalid_file = io.BytesIO(b"invalid_content")
        invalid_file.name = "test.txt"
        call_data["audio_file"] = invalid_file
        response = self.client.post("/api/calls/upload/", call_data, format="multipart")
        assert response.status_code == 400

    def test_evaluation_score_validations(self, setup_users, setup_form):
        """Değerlendirme puanlama validasyonları"""
        self.client.force_authenticate(user=self.expert)

        # Önce geçerli bir çağrı oluştur
        audio = io.BytesIO(b"file_content")
        audio.name = "test.mp3"
        call_data = {
            "agent": self.agent.id,
            "call_queue": self.queue.id,
            "phone_number": "5551234567",
            "call_date": datetime.datetime.now().isoformat(),
            "audio_file": audio,
        }
        call_response = self.client.post(
            "/api/calls/upload/", call_data, format="multipart"
        )
        call_id = call_response.data["id"]

        # Geçersiz puan değerleri ile değerlendirme
        invalid_scores = {
            "call": call_id,
            "form": setup_form,
            "scores": {"test1": 15, "test2": 11},  # Max 10 olmalıydı
            "final_note": "Test",
        }
        response = self.client.post("/api/evaluations/", invalid_scores, format="json")
        assert response.status_code == 400

    def test_duplicate_form_creation(self, setup_users):
        """Aynı isimle form oluşturma testi"""
        self.client.force_authenticate(user=self.admin)

        form_data = {
            "name": "Duplicate Form",
            "fields": [
                {"key": "test", "label": "Test", "type": "number", "max_score": 10}
            ],
        }

        # İlk oluşturma
        response1 = self.client.post("/api/evaluation-forms/", form_data, format="json")
        assert response1.status_code == 201

        # Aynı isimle tekrar oluşturma denemesi
        response2 = self.client.post("/api/evaluation-forms/", form_data, format="json")
        assert response2.status_code == 400
