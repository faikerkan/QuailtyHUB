from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from calls.models import EvaluationForm

User = get_user_model()

class Command(BaseCommand):
    help = 'Varsayılan değerlendirme formunu oluşturur'

    def handle(self, *args, **kwargs):
        # Süper kullanıcıyı al
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('Süper kullanıcı bulunamadı!'))
                return
            
            # Eğer form zaten varsa uyar
            if EvaluationForm.objects.exists():
                self.stdout.write(self.style.WARNING('Değerlendirme formu zaten mevcut!'))
                return
            
            # Varsayılan formu oluştur
            form = EvaluationForm.create_default_form(admin_user)
            self.stdout.write(self.style.SUCCESS(f'"{form.name}" başarıyla oluşturuldu!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Hata oluştu: {str(e)}')) 