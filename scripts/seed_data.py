#!/usr/bin/env python
import datetime
import os
import sys

import django

# Proje dizinini Python yoluna ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django ortamını kur
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "call_quality_hub.settings")
django.setup()

from django.contrib.auth import get_user_model

from calls.models import CallQueue, EvaluationForm

User = get_user_model()


def create_users():
    """Farklı rollere sahip örnek kullanıcılar oluşturur"""

    # Test kullanıcıları oluştur (eğer yoklarsa)
    users = [
        {
            "username": "admin",
            "email": "admin@callqualityhub.com",
            "password": "admin123",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
            "is_staff": True,
            "is_superuser": True,
        },
        {
            "username": "kalitetest",
            "email": "kalite@callqualityhub.com",
            "password": "kalite123",
            "first_name": "Kalite",
            "last_name": "Uzmanı",
            "role": "expert",
        },
        {
            "username": "agenttest",
            "email": "agent@callqualityhub.com",
            "password": "agent123",
            "first_name": "Müşteri",
            "last_name": "Temsilcisi",
            "role": "agent",
        },
    ]

    print("Kullanıcılar oluşturuluyor...")
    for user_data in users:
        username = user_data.pop("username")
        password = user_data.pop("password")

        user, created = User.objects.get_or_create(
            username=username, defaults=user_data
        )

        if created:
            user.set_password(password)
            user.save()
            print(f"  - {username} kullanıcısı oluşturuldu")
        else:
            print(f"  - {username} kullanıcısı zaten mevcut")


def create_call_queues():
    """Örnek çağrı kuyrukları oluşturur"""

    queues = [
        {
            "name": "Bireysel Müşteri Hizmetleri",
            "description": "Bireysel müşterilere hizmet veren müşteri temsilcileri için çağrı kuyruğu",
        },
        {
            "name": "Kurumsal Müşteri Hizmetleri",
            "description": "Kurumsal müşterilere hizmet veren müşteri temsilcileri için çağrı kuyruğu",
        },
        {
            "name": "Teknik Destek",
            "description": "Teknik sorunlar için destek sağlayan temsilciler için çağrı kuyruğu",
        },
        {
            "name": "Satış",
            "description": "Satış işlemleri için müşteri temsilcileri çağrı kuyruğu",
        },
    ]

    print("Çağrı kuyrukları oluşturuluyor...")
    for queue_data in queues:
        queue, created = CallQueue.objects.get_or_create(
            name=queue_data["name"], defaults={"description": queue_data["description"]}
        )

        if created:
            print(f"  - {queue.name} kuyruğu oluşturuldu")
        else:
            print(f"  - {queue.name} kuyruğu zaten mevcut")


def create_evaluation_forms():
    """Örnek değerlendirme formları oluşturur"""

    # Yönetici kullanıcısını al
    try:
        admin_user = User.objects.get(username="admin")
    except User.DoesNotExist:
        print("Hata: Admin kullanıcısı bulunamadı. Önce kullanıcıları oluşturun.")
        return

    # Varsayılan değerlendirme formu var mı kontrol et
    if not EvaluationForm.objects.filter(name="Standart Değerlendirme Formu").exists():
        try:
            EvaluationForm.create_default_form(admin_user)
            print("  - Standart Değerlendirme Formu oluşturuldu")
        except Exception as e:
            print(f"Hata: Değerlendirme formu oluşturulamadı: {str(e)}")
    else:
        print("  - Standart Değerlendirme Formu zaten mevcut")


def main():
    """Ana fonksiyon - tüm örnek verileri oluşturur"""
    print("CallQualityHub örnek veriler oluşturuluyor...")
    print("=============================================")

    create_users()
    create_call_queues()
    create_evaluation_forms()

    print("=============================================")
    print("Örnek veri oluşturma tamamlandı!")


if __name__ == "__main__":
    main()
