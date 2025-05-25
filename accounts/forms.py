from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser


class LoginForm(forms.Form):
    """
    Kullanıcı giriş formu
    """

    username = forms.CharField(
        label="Kullanıcı Adı",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Kullanıcı Adı"}
        ),
    )
    password = forms.CharField(
        label="Şifre",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Şifre"}
        ),
    )


class CustomUserCreationForm(UserCreationForm):
    """
    Yeni kullanıcı oluşturma formu
    """

    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "role")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})


class CustomUserChangeForm(UserChangeForm):
    """
    Kullanıcı bilgileri düzenleme formu
    """

    password = None  # Şifre değiştirmeyi ayrı bir görünümle yapacağız

    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "role", "is_active")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ProfileForm(forms.ModelForm):
    """
    Kullanıcı profil bilgileri düzenleme formu
    """

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
