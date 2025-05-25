from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from .models import UserProfile


@login_required
def dashboard(request):
    """Dashboard view for authenticated users"""
    return HttpResponse("Dashboard")


@login_required
def user_list(request):
    """List all users - admin only"""
    return HttpResponse("Kullanıcı Listesi")


@login_required
def user_create(request):
    """Create new user - admin only"""
    if not request.user.is_staff and request.user.userprofile.role != 'admin':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Basic user creation logic
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'agent')
        
        if username and email and password:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.userprofile.role = role
            user.userprofile.save()
            messages.success(request, 'Kullanıcı başarıyla oluşturuldu.')
            return redirect('user_list')
        else:
            messages.error(request, 'Tüm alanları doldurun.')
    
    return render(request, 'users/user_create.html')


@login_required
def user_edit(request, user_id):
    """Edit user - admin only"""
    if not request.user.is_staff and request.user.userprofile.role != 'admin':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Basic user edit logic
        user.email = request.POST.get('email', user.email)
        role = request.POST.get('role', user.userprofile.role)
        user.userprofile.role = role
        user.save()
        user.userprofile.save()
        messages.success(request, 'Kullanıcı başarıyla güncellendi.')
        return redirect('user_list')
    
    context = {'user_obj': user}
    return render(request, 'users/user_edit.html', context)


@login_required
def user_delete(request, user_id):
    """Delete user - admin only"""
    if not request.user.is_staff and request.user.userprofile.role != 'admin':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Kullanıcı başarıyla silindi.')
        return redirect('user_list')
    
    context = {'user_obj': user}
    return render(request, 'users/user_delete.html', context)


@login_required
def profile(request):
    """User profile view"""
    context = {
        'user': request.user,
        'profile': request.user.userprofile,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        # Basic profile edit logic
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()
        messages.success(request, 'Profil başarıyla güncellendi.')
        return redirect('profile')
    
    context = {
        'user': request.user,
        'profile': request.user.userprofile,
    }
    return render(request, 'users/profile_edit.html', context) 