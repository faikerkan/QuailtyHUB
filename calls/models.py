from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from decimal import Decimal

class CallQueue(models.Model):
    """
    Çağrı kuyrukları için model.
    Farklı operasyonlar için farklı kuyruklar tanımlanabilir.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Çağrı Kuyruğu"
        verbose_name_plural = "Çağrı Kuyrukları"
        ordering = ['name']

class EvaluationForm(models.Model):
    """
    Değerlendirme formları için model.
    Formlar dinamik olarak oluşturulabilir ve farklı operasyonlar için özelleştirilebilir.
    Form alanları JSON formatında saklanacaktır.
    
    Örnek form yapısı:
    {
        "field_1": {
            "label": "Açılış ve Karşılama",
            "type": "number",
            "max_score": 5
        },
        ...
    }
    """
    name = models.CharField(max_length=100, unique=True)
    fields = models.JSONField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_forms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Değerlendirme Formu"
        verbose_name_plural = "Değerlendirme Formları"
        ordering = ['-created_at']
        
    @classmethod
    def create_default_form(cls, user):
        """
        Varsayılan değerlendirme formunu oluşturur.
        """
        default_fields = {
            "field_1": {
                "label": "Açılış ve Karşılama",
                "type": "number",
                "max_score": 5
            },
            "field_2": {
                "label": "Etkin Dinleme ve Anlama",
                "type": "number",
                "max_score": 15
            },
            "field_3": {
                "label": "Analiz ve Etkin Soru Sorma",
                "type": "number",
                "max_score": 15
            },
            "field_4": {
                "label": "Görüşme Kirliliği Yaratacak Söylem ve Sesler",
                "type": "number",
                "max_score": 10
            },
            "field_5": {
                "label": "Kendinden Emin, Canlı ve Nezaketli Ses Tonu",
                "type": "number",
                "max_score": 10
            },
            "field_6": {
                "label": "Abonenin Sorununun Sahiplenilmesi",
                "type": "number",
                "max_score": 5
            },
            "field_7": {
                "label": "Empati",
                "type": "number",
                "max_score": 5
            },
            "field_8": {
                "label": "Süre ve Stres Yönetimi",
                "type": "number",
                "max_score": 5
            },
            "field_9": {
                "label": "Doğru Yönlendirme",
                "type": "number",
                "max_score": 10
            },
            "field_10": {
                "label": "Bilgiyi Anlaşılır Biçimde Paylaşma, İkna Etme",
                "type": "number",
                "max_score": 10
            },
            "field_11": {
                "label": "Uygun Kapanış Anonsu Verildi mi?",
                "type": "number",
                "max_score": 5
            },
            "field_12": {
                "label": "İlgili/Yönlendirilen Ekibe İlgili Bilgi Verildi mi?",
                "type": "number",
                "max_score": 5
            }
        }
        
        return cls.objects.create(
            name="Standart Değerlendirme Formu",
            created_by=user,
            fields=default_fields
        )

class CallRecord(models.Model):
    """
    Çağrı kayıtları için model.
    Ses dosyaları MP3 formatında saklanacaktır.
    """
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_calls'
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agent_calls'
    )
    call_queue = models.ForeignKey(
        CallQueue,
        on_delete=models.CASCADE,
        related_name='calls'
    )
    phone_number = models.CharField(max_length=20)
    audio_file = models.FileField(
        upload_to='call_records/',
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'm4a'])]
    )
    call_id = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    call_date = models.DateTimeField()
    
    def __str__(self):
        agent_name = self.agent.get_full_name() if self.agent else "Bilinmeyen"
        return f"Çağrı - {self.call_id} - {self.call_date}"
    
    class Meta:
        verbose_name = "Çağrı Kaydı"
        verbose_name_plural = "Çağrı Kayıtları"
        ordering = ['-call_date']

class Evaluation(models.Model):
    """
    Değerlendirme sonuçları için model.
    Değerlendirme puanları JSON formatında saklanacaktır.
    """
    call = models.ForeignKey(
        CallRecord,
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    form = models.ForeignKey(
        EvaluationForm,
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    scores = models.JSONField()
    final_note = models.TextField()
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    evaluated_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Toplam puanı hesapla
        total_points = Decimal('0')
        max_points = Decimal('0')

        if self.form and hasattr(self.form, 'fields'):
            for key, value in self.form.fields.items():
                max_score = Decimal(str(value.get('max_score', 0)))
                score = Decimal(str(self.scores.get(key, {}).get('score', 0)))
                total_points += score
                max_points += max_score

        if max_points > 0:
            self.total_score = ((total_points / max_points) * Decimal('100')).quantize(Decimal('0.01'))
        else:
            self.total_score = Decimal('0')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Değerlendirme - {self.call} - {self.evaluator}"
    
    class Meta:
        verbose_name = "Değerlendirme"
        verbose_name_plural = "Değerlendirmeler"
        ordering = ['-evaluated_at']
