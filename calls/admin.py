from django.contrib import admin

from .models import CallQueue, CallRecord, Evaluation, EvaluationForm


@admin.register(CallQueue)
class CallQueueAdmin(admin.ModelAdmin):
    """
    Çağrı kuyruğu yönetimi için admin arayüzü.
    """

    list_display = ["name", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at"]


@admin.register(EvaluationForm)
class EvaluationFormAdmin(admin.ModelAdmin):
    """
    Değerlendirme formu yönetimi için admin arayüzü.
    """

    list_display = ["name", "created_by", "created_at", "get_total_points"]
    list_filter = ["created_at", "created_by"]
    search_fields = ["name"]
    readonly_fields = ["created_at"]

    def get_total_points(self, obj):
        """Formun toplam puan değerini hesaplar."""
        total = sum(field.get("max_score", 0) for field in obj.fields.values())
        return f"{total} Puan"

    get_total_points.short_description = "Toplam Puan"

    def save_model(self, request, obj, form, change):
        """Yeni form oluşturulurken created_by alanını otomatik doldur."""
        if not change:  # Yeni kayıt ise
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CallRecord)
class CallRecordAdmin(admin.ModelAdmin):
    """
    Çağrı kaydı yönetimi için admin arayüzü.
    """

    list_display = ["agent", "call_queue", "phone_number", "call_date", "uploaded_at"]
    list_filter = ["call_date", "uploaded_at", "agent", "call_queue"]
    search_fields = [
        "agent__username",
        "agent__first_name",
        "agent__last_name",
        "call_id",
        "phone_number",
    ]
    readonly_fields = ["uploaded_at"]


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    """
    Değerlendirme yönetimi için admin arayüzü.
    """

    list_display = ["call", "evaluator", "total_score", "evaluated_at"]
    list_filter = ["evaluated_at", "evaluator"]
    search_fields = ["call__agent__username", "evaluator__username", "final_note"]
    readonly_fields = ["evaluated_at"]
