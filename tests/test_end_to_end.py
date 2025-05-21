import pytest
from django.urls import reverse
from accounts.models import CustomUser
from calls.models import CallRecord, EvaluationForm, Evaluation, CallQueue
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import datetime
from decimal import Decimal

@pytest.mark.django_db
class TestEndToEnd:
    @pytest.fixture
    def setup_test_data(self):
        # Test kullanıcılarını oluştur
        self.admin = CustomUser.objects.create_user(
            username='admin', 
            password='admin123', 
            role='admin', 
            is_superuser=True, 
            is_staff=True
        )
        self.expert = CustomUser.objects.create_user(
            username='kalitetest', 
            password='kalite123', 
            role='expert'
        )
        self.agent = CustomUser.objects.create_user(
            username='agenttest', 
            password='agent123', 
            role='agent'
        )
        self.queue = CallQueue.objects.create(name="Test Queue")
        return self.admin, self.expert, self.agent, self.queue

    def test_basic_evaluation_flow(self, client, setup_test_data):
        """Temel değerlendirme akışı testi"""
        # Yönetici ile giriş yap
        client.login(username='admin', password='admin123')

        # Değerlendirme formu oluştur
        form = EvaluationForm.objects.create(
            name="Standart Değerlendirme",
            created_by=self.admin,
            fields=[
                {"key": "greeting", "label": "Selamlama", "type": "number", "max_score": 10},
                {"key": "problem_solving", "label": "Çözüm Üretme", "type": "number", "max_score": 20}
            ]
        )

        # Kalite uzmanı ile giriş yap
        client.logout()
        client.login(username='kalitetest', password='kalite123')

        # Çağrı kaydı yükle
        audio = SimpleUploadedFile("test.mp3", b"file_content", content_type="audio/mp3")
        call = CallRecord.objects.create(
            uploaded_by=self.expert,
            agent=self.agent,
            call_queue=self.queue,
            audio_file=audio,
            phone_number="5551234567",
            call_date=datetime.datetime.now()
        )

        # Değerlendirme ekle
        evaluation = Evaluation.objects.create(
            call=call,
            evaluator=self.expert,
            form=form,
            scores={"greeting": 8, "problem_solving": 18},
            final_note="Başarılı iletişim"
        )

        # Agent ile giriş yapıp kontrolleri gerçekleştir
        client.logout()
        client.login(username='agenttest', password='agent123')
        
        # Çağrıları kontrol et
        my_calls = CallRecord.objects.filter(agent=self.agent)
        assert my_calls.count() == 1
        assert my_calls.first().phone_number == "5551234567"
        filename = my_calls.first().audio_file.name
        assert filename.endswith(".mp3")
        assert "test" in filename

        # Değerlendirmeleri kontrol et
        my_evaluations = Evaluation.objects.filter(call__agent=self.agent)
        assert my_evaluations.count() == 1
        assert my_evaluations.first().final_note == "Başarılı iletişim"
        assert my_evaluations.first().total_score == Decimal('86.67')  # (8/10 + 18/20) * 100 / 2

    def test_multiple_agents_flow(self, client, setup_test_data):
        """Çoklu agent değerlendirme akışı testi"""
        # İkinci bir agent oluştur
        agent2 = CustomUser.objects.create_user(
            username='agent2test',
            password='agent123',
            role='agent'
        )

        # Yönetici ile form oluştur
        client.login(username='admin', password='admin123')
        form = EvaluationForm.objects.create(
            name="Çoklu Agent Formu",
            created_by=self.admin,
            fields=[
                {"key": "quality", "label": "Kalite", "type": "number", "max_score": 10}
            ]
        )

        # Kalite uzmanı ile çağrı ve değerlendirmeler oluştur
        client.logout()
        client.login(username='kalitetest', password='kalite123')

        # Her agent için ikişer çağrı oluştur
        for agent in [self.agent, agent2]:
            for i in range(2):
                # Çağrı oluştur
                audio = SimpleUploadedFile(f"test_{agent.username}_{i}.mp3", b"file_content", content_type="audio/mp3")
                call = CallRecord.objects.create(
                    uploaded_by=self.expert,
                    agent=agent,
                    call_queue=self.queue,
                    audio_file=audio,
                    phone_number=f"55512345{i}{agent.id}",
                    call_date=datetime.datetime.now()
                )

                # Değerlendirme oluştur
                Evaluation.objects.create(
                    call=call,
                    evaluator=self.expert,
                    form=form,
                    scores={"quality": 7 + i},
                    final_note=f"Test değerlendirme {agent.username} {i}"
                )

        # Her agent için kontroller
        for agent in [self.agent, agent2]:
            # Agent'ın çağrılarını kontrol et
            agent_calls = CallRecord.objects.filter(agent=agent)
            assert agent_calls.count() == 2

            # Agent'ın değerlendirmelerini kontrol et
            agent_evals = Evaluation.objects.filter(call__agent=agent).order_by('evaluated_at')
            assert agent_evals.count() == 2

            # Puanları kontrol et
            scores = [eval.total_score for eval in agent_evals]
            assert sorted(scores) == [Decimal('70.00'), Decimal('80.00')]  # 7/10 ve 8/10 * 100

    def test_form_versioning_flow(self, client, setup_test_data):
        """Form versiyonlama akışı testi"""
        # Yönetici ile giriş yap
        client.login(username='admin', password='admin123')

        # İlk versiyon form
        form_v1 = EvaluationForm.objects.create(
            name="Form v1",
            created_by=self.admin,
            fields=[
                {"key": "quality", "label": "Kalite", "type": "number", "max_score": 10}
            ]
        )

        # İkinci versiyon form (farklı puanlama)
        form_v2 = EvaluationForm.objects.create(
            name="Form v2",
            created_by=self.admin,
            fields=[
                {"key": "quality", "label": "Kalite", "type": "number", "max_score": 20}
            ]
        )

        # Kalite uzmanı ile değerlendirmeler yap
        client.logout()
        client.login(username='kalitetest', password='kalite123')

        # Her form versiyonu için bir çağrı ve değerlendirme
        for form in [form_v1, form_v2]:
            # Çağrı oluştur
            audio = SimpleUploadedFile(f"test_{form.name}.mp3", b"file_content", content_type="audio/mp3")
            call = CallRecord.objects.create(
                uploaded_by=self.expert,
                agent=self.agent,
                call_queue=self.queue,
                audio_file=audio,
                phone_number=f"5551234{form.id}",
                call_date=datetime.datetime.now()
            )

            # Değerlendirme oluştur (her formda maksimum puan)
            max_score = form.fields[0]['max_score']
            Evaluation.objects.create(
                call=call,
                evaluator=self.expert,
                form=form,
                scores={"quality": max_score},
                final_note=f"Test değerlendirme {form.name}"
            )

        # Değerlendirmeleri kontrol et
        evaluations = Evaluation.objects.filter(call__agent=self.agent).order_by('form__name')
        
        # Her iki değerlendirme de %100 puan almalı
        assert len(evaluations) == 2
        for eval in evaluations:
            assert eval.total_score == Decimal('100.00') 