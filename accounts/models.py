from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Özel kullanıcı modeli. Yönetici, Kalite Uzmanı ve Müşteri Temsilcisi
    rollerini destekler.
    """
    ROLE_CHOICES = [
        ('admin', 'Yönetici'),
        ('expert', 'Kalite Uzmanı'),
        ('agent', 'Müşteri Temsilcisi'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    def is_admin(self):
        """Kullanıcının yönetici olup olmadığını kontrol eder."""
        return self.role == 'admin'
    
    def is_expert(self):
        """Kullanıcının kalite uzmanı olup olmadığını kontrol eder."""
        return self.role == 'expert'
    
    def is_agent(self):
        """Kullanıcının müşteri temsilcisi olup olmadığını kontrol eder."""
        return self.role == 'agent'
