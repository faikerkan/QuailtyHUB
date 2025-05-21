from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import CustomUser
from .forms import LoginForm, CustomUserCreationForm, CustomUserChangeForm, ProfileForm

def login_view(request):
    """
    Kullanıcı giriş işlemini gerçekleştirir.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Kullanıcı adı veya şifre hatalı!')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """
    Kullanıcı çıkış işlemini gerçekleştirir.
    """
    logout(request)
    return redirect('accounts:login')

@login_required
def profile_view(request):
    """
    Kullanıcı profil bilgilerini görüntüleme ve düzenleme.
    """
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil bilgileriniz başarıyla güncellendi.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def user_list(request):
    """
    Kullanıcı listesini görüntüleme (sadece yöneticiler için).
    """
    if not (request.user.is_superuser or request.user.is_admin()):
        return HttpResponseForbidden("Bu sayfaya erişim izniniz yok.")
    
    users = CustomUser.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
def user_create(request):
    """
    Yeni kullanıcı oluşturma (sadece yöneticiler için).
    """
    if not (request.user.is_superuser or request.user.is_admin()):
        return HttpResponseForbidden("Bu sayfaya erişim izniniz yok.")
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kullanıcı başarıyla oluşturuldu.')
            return redirect('accounts:user_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Yeni Kullanıcı Oluştur'})

@login_required
def user_edit(request, user_id):
    """
    Kullanıcı bilgilerini düzenleme (sadece yöneticiler için).
    """
    if not (request.user.is_superuser or request.user.is_admin()):
        return HttpResponseForbidden("Bu sayfaya erişim izniniz yok.")
    
    user = CustomUser.objects.get(id=user_id)
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kullanıcı bilgileri başarıyla güncellendi.')
            return redirect('accounts:user_list')
    else:
        form = CustomUserChangeForm(instance=user)
    
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Kullanıcı Düzenle'})

@login_required
def user_delete(request, user_id):
    """
    Kullanıcı silme (sadece yöneticiler için).
    """
    if not (request.user.is_superuser or request.user.is_admin()):
        return HttpResponseForbidden("Bu sayfaya erişim izniniz yok.")
    
    user = CustomUser.objects.get(id=user_id)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Kullanıcı başarıyla silindi.')
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_delete.html', {'user': user})

@login_required
def password_change(request):
    """
    Kullanıcının kendi şifresini değiştirmesi için görünüm.
    """
    if request.method == 'POST':
        # Django'nun PasswordChangeForm kullanılabilir
        # Şimdilik basit bir implementasyon gösteriyoruz
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(current_password):
            messages.error(request, 'Mevcut şifreniz yanlış.')
            return redirect('accounts:password_change')
        
        if new_password != confirm_password:
            messages.error(request, 'Yeni şifreler eşleşmiyor.')
            return redirect('accounts:password_change')
        
        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, 'Şifreniz başarıyla değiştirildi.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/password_change.html')
