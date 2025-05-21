import pytest
from django.contrib.auth import get_user_model
from calls.models import CallQueue, CallRecord, Evaluation, EvaluationForm
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

@pytest.fixture(scope="function", autouse=True)
def create_test_users_and_data(db, tmp_path):
    # Kullanıcılar
    if not User.objects.filter(username="admin").exists():
        admin = User.objects.create_superuser(username="admin", password="admin123", email="admin@example.com", role="admin", is_staff=True, is_superuser=True)
    else:
        admin = User.objects.get(username="admin")
    if not User.objects.filter(username="kalitetest").exists():
        kalite = User.objects.create_user(username="kalitetest", password="kalite123", email="kalite@example.com", role="expert")
    else:
        kalite = User.objects.get(username="kalitetest")
    if not User.objects.filter(username="agenttest").exists():
        agent = User.objects.create_user(username="agenttest", password="agent123", email="agent@example.com", role="agent")
    else:
        agent = User.objects.get(username="agenttest")
    # Ek kullanıcılar
    if not User.objects.filter(username="user1").exists():
        User.objects.create_user(username="user1", password="user123", email="user1@example.com", role="agent")
    if not User.objects.filter(username="user2").exists():
        User.objects.create_user(username="user2", password="user123", email="user2@example.com", role="expert")

    # Çağrı Kuyruğu
    queue, _ = CallQueue.objects.get_or_create(name="Test Kuyruğu", defaults={"description": "Test için otomatik oluşturuldu."})

    # Çağrı Kaydı (örnek ses dosyası olmadan, zorunluysa küçük bir dosya oluşturulabilir)
    call_date = timezone.now() - timedelta(days=1)
    call, _ = CallRecord.objects.get_or_create(
        agent=agent,
        call_queue=queue,
        phone_number="5551234567",
        call_date=call_date,
        uploaded_by=admin,
        defaults={
            "audio_file": "call_records/test.mp3",
            "call_id": "TESTCALL1"
        }
    )

    # Değerlendirme Formu (varsa tekrar oluşturma)
    form = EvaluationForm.objects.first()
    if not form:
        form = EvaluationForm.create_default_form(admin)

    # Değerlendirme (varsa tekrar oluşturma)
    if not Evaluation.objects.filter(call=call).exists():
        scores = {key: {"score": value.get("max_score", 5), "max_score": value.get("max_score", 5), "label": value.get("label", key)} for key, value in form.fields.items()}
        Evaluation.objects.create(
            call=call,
            evaluator=kalite,
            form=form,
            scores=scores,
            final_note="Otomatik test değerlendirmesi.",
            total_score=100
        ) 