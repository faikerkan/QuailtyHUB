from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Max, Min, Q
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils import timezone

from accounts.models import CustomUser
from calls.models import CallQueue, CallRecord, Evaluation, EvaluationForm

# Create your views here.


@login_required
def index(request):
    """
    Kullanıcıya özel ana sayfa (dashboard landing).
    """
    user = request.user
    if user.is_superuser or (hasattr(user, "is_admin") and user.is_admin()):
        return redirect("dashboard:admin_dashboard")
    elif hasattr(user, "is_expert") and user.is_expert():
        return redirect("dashboard:expert_dashboard")
    elif hasattr(user, "is_agent") and user.is_agent():
        return redirect("dashboard:agent_dashboard")
    # Diğer roller için default bir sayfa veya hata
    return render(request, "dashboard/index.html", {"title": "Ana Sayfa"})


@login_required
def admin_dashboard(request):
    """
    Yönetici rolüne sahip kullanıcılar için dashboard.
    """
    if not (
        request.user.is_superuser
        or (hasattr(request.user, "is_admin") and request.user.is_admin())
    ):
        return HttpResponseForbidden("Bu sayfaya erişim izniniz yok.")

    user_count = CustomUser.objects.count()
    call_count = CallRecord.objects.count()
    evaluation_count = Evaluation.objects.count()
    form_count = EvaluationForm.objects.count()
    avg_score = Evaluation.objects.aggregate(avg=Avg("total_score"))["avg"] or 0

    # Son 7 gün değerlendirme sayısı (grafik için)
    today = timezone.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    evals_by_day = (
        Evaluation.objects.filter(evaluated_at__date__gte=last_7_days[-1])
        .values("evaluated_at__date")
        .annotate(count=Count("id"))
    )
    evals_by_day_dict = {e["evaluated_at__date"]: e["count"] for e in evals_by_day}
    evals_chart = [evals_by_day_dict.get(day, 0) for day in last_7_days]

    context = {
        "title": "Yönetici Paneli",
        "user_count": user_count,
        "call_count": call_count,
        "evaluation_count": evaluation_count,
        "form_count": form_count,
        "avg_score": round(avg_score, 1),
        "evals_chart": evals_chart,
        "evals_chart_labels": [day.strftime("%d.%m") for day in last_7_days],
    }
    return render(request, "dashboard/admin_dashboard.html", context)


@login_required
def expert_dashboard(request):
    """
    Kalite Uzmanı rolüne sahip kullanıcılar için dashboard.
    """
    if not (hasattr(request.user, "is_expert") and request.user.is_expert()):
        return HttpResponseForbidden("Bu sayfaya erişim izniniz yok.")

    today = timezone.now().date()
    month_start = today.replace(day=1)
    # Bekleyen çağrılar: henüz değerlendirilmemiş çağrılar
    evaluated_call_ids = Evaluation.objects.filter(evaluator=request.user).values_list(
        "call_id", flat=True
    )
    pending_calls = CallRecord.objects.filter(
        ~Q(id__in=Evaluation.objects.values_list("call_id", flat=True))
    ).order_by("-call_date")[:5]
    # Son değerlendirmeler
    recent_evaluations = Evaluation.objects.filter(evaluator=request.user).order_by(
        "-evaluated_at"
    )[:5]
    # İstatistikler
    total_evaluations = Evaluation.objects.filter(evaluator=request.user).count()
    this_month_evaluations = Evaluation.objects.filter(
        evaluator=request.user, evaluated_at__date__gte=month_start
    ).count()
    avg_score = (
        Evaluation.objects.filter(evaluator=request.user).aggregate(
            avg=Avg("total_score")
        )["avg"]
        or 0
    )
    context = {
        "title": "Kalite Uzmanı Paneli",
        "pending_calls": pending_calls,
        "recent_evaluations": recent_evaluations,
        "total_evaluations": total_evaluations,
        "this_month_evaluations": this_month_evaluations,
        "avg_score": round(avg_score, 1),
    }
    return render(request, "dashboard/expert_dashboard.html", context)


@login_required
def agent_dashboard(request):
    """
    Müşteri Temsilcisi rolüne sahip kullanıcılar için dashboard.
    """
    if not (hasattr(request.user, "is_agent") and request.user.is_agent()):
        return HttpResponseForbidden("Bu sayfaya erişim izniniz yok.")
    from django.db.models import Avg

    from calls.models import CallRecord, Evaluation

    # Kendi çağrıları
    my_calls = CallRecord.objects.filter(agent=request.user).order_by("-call_date")[:5]
    # Kendi çağrılarının değerlendirmeleri
    my_evaluations = Evaluation.objects.filter(call__agent=request.user).order_by(
        "-evaluated_at"
    )[:5]
    # Ortalama puan
    avg_score = (
        Evaluation.objects.filter(call__agent=request.user).aggregate(
            avg=Avg("total_score")
        )["avg"]
        or 0
    )
    context = {
        "title": "Müşteri Temsilcisi Paneli",
        "my_calls": my_calls,
        "my_evaluations": my_evaluations,
        "avg_score": round(avg_score, 1),
    }
    return render(request, "dashboard/agent_dashboard.html", context)


@login_required
def admin_reports(request):
    """
    Yönetici için detaylı raporlar ve analiz ekranı.
    """
    if not (
        request.user.is_superuser
        or (hasattr(request.user, "is_admin") and request.user.is_admin())
    ):
        return HttpResponseForbidden("Bu sayfaya erişim izniniz yok.")
    # Filtreler
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    agent_id = request.GET.get("agent")
    expert_id = request.GET.get("expert")
    queue_id = request.GET.get("queue")
    evals = Evaluation.objects.select_related(
        "call", "evaluator", "call__agent", "call__call_queue"
    )
    if start_date:
        evals = evals.filter(evaluated_at__date__gte=start_date)
    if end_date:
        evals = evals.filter(evaluated_at__date__lte=end_date)
    if agent_id:
        evals = evals.filter(call__agent_id=agent_id)
    if expert_id:
        evals = evals.filter(evaluator_id=expert_id)
    if queue_id:
        evals = evals.filter(call__call_queue_id=queue_id)
    # Temsilci performansı
    agent_stats = (
        evals.values(
            "call__agent__id", "call__agent__first_name", "call__agent__last_name"
        )
        .annotate(
            total=Count("id"),
            avg_score=Avg("total_score"),
            last_eval=Max("evaluated_at"),
            min_score=Min("total_score"),
            max_score=Max("total_score"),
        )
        .order_by("-avg_score")
    )
    # Kalite uzmanı performansı
    expert_stats = (
        evals.values("evaluator__id", "evaluator__first_name", "evaluator__last_name")
        .annotate(
            total=Count("id"),
            avg_score=Avg("total_score"),
            last_eval=Max("evaluated_at"),
        )
        .order_by("-total")
    )
    # Operasyonel özet
    total_evals = evals.count()
    avg_score = evals.aggregate(avg=Avg("total_score"))["avg"] or 0
    most_active_agent = agent_stats.first() if agent_stats else None
    most_active_expert = expert_stats.first() if expert_stats else None
    agents = CustomUser.objects.filter(role="agent")
    experts = CustomUser.objects.filter(role="expert")
    queues = CallQueue.objects.all()
    context = {
        "title": "Detaylı Raporlar",
        "agent_stats": agent_stats,
        "expert_stats": expert_stats,
        "total_evals": total_evals,
        "avg_score": round(avg_score, 1),
        "most_active_agent": most_active_agent,
        "most_active_expert": most_active_expert,
        "agents": agents,
        "experts": experts,
        "queues": queues,
        "start_date": start_date,
        "end_date": end_date,
        "selected_agent": int(agent_id) if agent_id else None,
        "selected_expert": int(expert_id) if expert_id else None,
        "selected_queue": int(queue_id) if queue_id else None,
    }
    return render(request, "dashboard/admin_reports.html", context)
