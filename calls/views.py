from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import CallRecord, Evaluation, EvaluationForm, CallQueue
from .forms import CallRecordForm, EvaluationCreateForm
from django.core.paginator import Paginator

@login_required
def call_list(request):
    """
    Çağrı kayıtlarının listesini gösterir.
    """
    # Kullanıcı rolüne göre çağrıları filtrele
    if request.user.is_admin() or request.user.is_superuser:
        # Yöneticiler tüm çağrıları görebilir
        calls = CallRecord.objects.all().order_by('-call_date')
    elif request.user.is_expert():
        # Kalite uzmanları henüz değerlendirilmemiş çağrıları ve kendi değerlendirdiklerini görebilir
        evaluated_call_ids = Evaluation.objects.filter(
            evaluator=request.user
        ).values_list('call_id', flat=True)
        
        calls = CallRecord.objects.filter(
            Q(id__in=evaluated_call_ids) | 
            ~Q(id__in=Evaluation.objects.values_list('call_id', flat=True))
        ).order_by('-call_date')
    else:
        # Müşteri temsilcileri sadece kendi çağrılarını görebilir
        calls = CallRecord.objects.filter(agent=request.user).order_by('-call_date')
    
    return render(request, 'calls/call_list.html', {
        'calls': calls,
        'title': 'Çağrı Kayıtları'
    })

@login_required
def call_detail(request, call_id):
    """
    Çağrı kaydının detaylarını ve değerlendirmelerini gösterir.
    """
    call = get_object_or_404(CallRecord, id=call_id)
    
    # Erişim kontrolü
    if not (request.user.is_admin() or request.user.is_superuser or
            request.user.is_expert() or request.user == call.agent):
        return HttpResponseForbidden("Bu sayfaya erişim izniniz yok.")
    
    evaluations = Evaluation.objects.filter(call=call).order_by('-evaluated_at')
    
    return render(request, 'calls/call_detail.html', {
        'call': call,
        'evaluations': evaluations,
        'title': f'Çağrı Detayı - {call}'
    })

@login_required
def call_upload(request):
    """
    Yeni çağrı kaydı yükleme sayfası.
    """
    if not (request.user.is_admin() or request.user.is_superuser or request.user.is_expert()):
        return HttpResponseForbidden("Bu sayfaya erişim izniniz yok.")
    
    if request.method == 'POST':
        form = CallRecordForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            call_record = form.save(commit=False)
            call_record.uploaded_by = request.user
            call_record.save()
            
            messages.success(request, "Çağrı kaydı başarıyla yüklendi.")
            return redirect('calls:evaluate', call_id=call_record.id)
    else:
        form = CallRecordForm(user=request.user)
    
    return render(request, 'calls/call_upload.html', {
        'form': form,
        'title': 'Çağrı Kaydı Yükle'
    })

@login_required
def evaluate(request, call_id):
    """
    Çağrı değerlendirme sayfası.
    """
    if not (request.user.is_admin() or request.user.is_superuser or request.user.is_expert()):
        messages.error(request, "Bu sayfaya erişim izniniz yok.")
        return redirect('calls:call_list')
    
    call = get_object_or_404(CallRecord, id=call_id)
    
    # Mevcut değerlendirme kontrolü
    if Evaluation.objects.filter(call=call).exists():
        messages.warning(request, "Bu çağrı zaten değerlendirilmiş.")
        return redirect('calls:call_detail', call_id=call.id)
    
    # Değerlendirme formunu seç
    evaluation_form = EvaluationForm.objects.first()
    
    if not evaluation_form:
        messages.error(request, "Değerlendirme formu bulunamadı. Lütfen önce bir form oluşturun.")
        return redirect('calls:call_list')
    
    return render(request, 'calls/evaluate.html', {
        'form': None,  # API tabanlı form kullanıldığı için None
        'call': call,
        'evaluation_form': evaluation_form,
        'title': f'Değerlendirme - {call}'
    })

@login_required
def evaluation_detail(request, evaluation_id):
    """
    Değerlendirme detaylarını gösterir.
    """
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    
    # Erişim kontrolü
    if not (request.user.is_admin() or request.user.is_superuser or
            request.user == evaluation.evaluator or request.user == evaluation.call.agent):
        return HttpResponseForbidden("Bu sayfaya erişim izniniz yok.")
    
    return render(request, 'calls/evaluation_detail.html', {
        'evaluation': evaluation,
        'title': f'Değerlendirme Detayı - {evaluation}'
    })

@login_required
def my_evaluations(request):
    """
    Kalite uzmanı için yaptığı değerlendirmeleri listeler.
    """
    if not (hasattr(request.user, 'is_expert') and request.user.is_expert()):
        return HttpResponseForbidden("Bu sayfaya erişim izniniz yok.")
    from calls.models import Evaluation
    evaluations = Evaluation.objects.filter(evaluator=request.user).order_by('-evaluated_at')
    paginator = Paginator(evaluations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': 'Değerlendirmelerim',
        'evaluations': page_obj,
    }
    return render(request, 'calls/my_evaluations.html', context)
