import datetime
import io

import pytest
from rest_framework.test import APIClient

from accounts.models import CustomUser
from calls.models import CallQueue, EvaluationForm


@pytest.mark.django_db
class TestAPIEndToEnd:
    @pytest.fixture
    def setup_test_data(self):
        # Test verilerini temizle
        EvaluationForm.objects.all().delete()

        # Test kullanıcılarını oluştur
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
        self.queue = CallQueue.objects.create(name="Satış")
        self.client = APIClient()

        return self.admin, self.expert, self.agent, self.queue

    def test_complete_evaluation_flow(self, setup_test_data):
        """Tam bir değerlendirme akışı testi"""
        # Admin ile giriş yap ve form oluştur
        self.client.force_authenticate(user=self.admin)
        form_data = {
            "name": "Standart Değerlendirme",
            "fields": [
                {
                    "key": "greeting",
                    "label": "Selamlama",
                    "type": "number",
                    "max_score": 10,
                },
                {
                    "key": "problem_solving",
                    "label": "Çözüm Üretme",
                    "type": "number",
                    "max_score": 20,
                },
            ],
        }
        form_response = self.client.post(
            "/api/evaluation-forms/", form_data, format="json"
        )
        assert form_response.status_code == 201
        form_id = form_response.data["id"]

        # Kalite uzmanı ile giriş yap ve çağrı yükle
        self.client.force_authenticate(user=self.expert)
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
        assert call_response.status_code in [200, 201]
        call_id = call_response.data["id"]

        # Değerlendirme ekle
        eval_data = {
            "call": call_id,
            "form": form_id,
            "scores": {"greeting": 8, "problem_solving": 18},
            "final_note": "Başarılı iletişim",
        }
        eval_response = self.client.post("/api/evaluations/", eval_data, format="json")
        assert eval_response.status_code in [200, 201]
        assert eval_response.data["total_score"] == 86.67  # (8/10 + 18/20) * 100 / 2

        # Agent ile giriş yap ve kendi çağrılarını kontrol et
        self.client.force_authenticate(user=self.agent)
        calls_response = self.client.get("/api/calls/")
        assert calls_response.status_code == 200
        calls = (
            calls_response.data["results"]
            if "results" in calls_response.data
            else calls_response.data
        )
        assert len(calls) == 1
        assert calls[0]["phone_number"] == "5551234567"

        # Değerlendirme sonuçlarını kontrol et
        evals_response = self.client.get(
            f"/api/evaluations/{eval_response.data['id']}/"
        )
        assert evals_response.status_code == 200
        assert evals_response.data["final_note"] == "Başarılı iletişim"

    def test_multiple_evaluations_flow(self, setup_test_data):
        """Birden fazla değerlendirme akışı testi"""
        # Admin ile form oluştur
        self.client.force_authenticate(user=self.admin)
        form_data = {
            "name": "Çoklu Değerlendirme Formu",
            "fields": [
                {"key": "quality", "label": "Kalite", "type": "number", "max_score": 10}
            ],
        }
        form_response = self.client.post(
            "/api/evaluation-forms/", form_data, format="json"
        )
        form_id = form_response.data["id"]

        # Kalite uzmanı ile çoklu çağrı ve değerlendirme oluştur
        self.client.force_authenticate(user=self.expert)
        created_calls = []

        for i in range(3):
            # Çağrı oluştur
            audio = io.BytesIO(b"file_content")
            audio.name = f"test_{i}.mp3"
            call_data = {
                "agent": self.agent.id,
                "call_queue": self.queue.id,
                "phone_number": f"555123456{i}",
                "call_date": datetime.datetime.now().isoformat(),
                "audio_file": audio,
            }
            call_response = self.client.post(
                "/api/calls/upload/", call_data, format="multipart"
            )
            assert call_response.status_code in [200, 201]
            created_calls.append(call_response.data["id"])

            # Değerlendirme oluştur
            eval_data = {
                "call": call_response.data["id"],
                "form": form_id,
                "scores": {"quality": 7 + i},  # Her değerlendirmede farklı puan
                "final_note": f"Test değerlendirme {i}",
            }
            eval_response = self.client.post(
                "/api/evaluations/", eval_data, format="json"
            )
            assert eval_response.status_code in [200, 201]

        # Agent'ın tüm çağrılarını kontrol et
        self.client.force_authenticate(user=self.agent)
        calls_response = self.client.get("/api/calls/")
        assert calls_response.status_code == 200
        calls = (
            calls_response.data["results"]
            if "results" in calls_response.data
            else calls_response.data
        )
        assert len(calls) == 3

        # Değerlendirmeleri kontrol et
        evals_response = self.client.get("/api/evaluations/")
        assert evals_response.status_code == 200
        evals = (
            evals_response.data["results"]
            if "results" in evals_response.data
            else evals_response.data
        )
        assert len(evals) == 3

        # Puanların doğruluğunu kontrol et
        scores = [eval_data["total_score"] for eval_data in evals]
        assert sorted(scores) == [70.0, 80.0, 90.0]  # 7/10, 8/10, 9/10 * 100
