import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'call_quality_hub.settings')
django.setup()

from calls.models import EvaluationForm
from django.db import transaction

with transaction.atomic():
    forms = EvaluationForm.objects.all()
    changed = 0
    for form in forms:
        if isinstance(form.fields, list):
            # Listeyi dict'e çevir
            new_fields = {f.get('key', f'field_{i+1}'): {k: v for k, v in f.items() if k != 'key'} for i, f in enumerate(form.fields)}
            form.fields = new_fields
            form.save()
            changed += 1
    print(f"Dönüştürülen form sayısı: {changed}") 