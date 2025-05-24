from django.shortcuts import render
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from accounts.models import CustomUser
from .serializers import (
    UserListSerializer, UserDetailSerializer, 
    UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer
)
from .permissions import IsAdminOrSuperUser, IsExpertOrAdmin
from calls.models import CallRecord, Evaluation, EvaluationForm
from .serializers import CallRecordSerializer, CallRecordUploadSerializer, EvaluationSerializer, EvaluationCreateSerializer, EvaluationFormSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
import os

class UserViewSet(viewsets.ModelViewSet):
    """
    Kullanıcı API görünümü
    
    list:
    Tüm kullanıcıları listeler (sadece yöneticiler erişebilir)
    
    retrieve:
    Belirli bir kullanıcının detaylarını gösterir (sadece yöneticiler erişebilir)
    
    create:
    Yeni bir kullanıcı oluşturur (sadece yöneticiler erişebilir)
    
    update:
    Bir kullanıcıyı günceller (sadece yöneticiler erişebilir)
    
    destroy:
    Bir kullanıcıyı siler (sadece yöneticiler erişebilir)
    """
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperUser]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserListSerializer
    
    @action(detail=True, methods=['post'], url_path='change-password')
    def change_password(self, request, pk=None):
        """
        Kullanıcı şifresini değiştirir
        """
        user = self.get_object()
        serializer = PasswordChangeSerializer(data=request.data)
        
        if serializer.is_valid():
            # Mevcut şifreyi kontrol et
            if not user.check_password(serializer.validated_data['current_password']):
                return Response(
                    {"current_password": ["Mevcut şifre yanlış."]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Şifreyi güncelle
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"status": "Şifre başarıyla değiştirildi"})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Giriş yapmış kullanıcının bilgilerini döndürür
        """
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def update_me(self, request):
        """
        Giriş yapan kullanıcı kendi profilini günceller
        """
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='me/change-password', permission_classes=[permissions.IsAuthenticated])
    def change_my_password(self, request):
        """
        Giriş yapan kullanıcı kendi şifresini değiştirir
        """
        serializer = PasswordChangeSerializer(data=request.data)
        user = request.user
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({"current_password": ["Mevcut şifre yanlış."]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"status": "Şifre başarıyla değiştirildi"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CallRecordViewSet(viewsets.ModelViewSet):
    queryset = CallRecord.objects.all().order_by('-call_date')
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'upload':
            return CallRecordUploadSerializer
        return CallRecordSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'is_admin') and (user.is_admin() or user.is_superuser):
            return CallRecord.objects.all().order_by('-call_date')
        elif hasattr(user, 'is_expert') and user.is_expert():
            return CallRecord.objects.all().order_by('-call_date')
        else:
            return CallRecord.objects.filter(agent=user).order_by('-call_date')

    @action(detail=False, methods=['post'], url_path='upload', permission_classes=[IsExpertOrAdmin])
    def upload(self, request):
        # Dosya formatı kontrolü
        if 'audio_file' not in request.FILES:
            return Response(
                {'audio_file': ['Bu alan zorunludur.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['audio_file']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.mp3', '.wav', '.m4a']:
            return Response(
                {'audio_file': ['Sadece .mp3, .wav ve .m4a dosyaları yüklenebilir.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CallRecordUploadSerializer(data=request.data)
        if serializer.is_valid():
            call_record = serializer.save(uploaded_by=request.user)
            return Response(
                CallRecordSerializer(call_record, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EvaluationFormViewSet(viewsets.ModelViewSet):
    """
    Değerlendirme formları için API görünümü.
    """
    queryset = EvaluationForm.objects.all()
    serializer_class = EvaluationFormSerializer
    permission_classes = [permissions.AllowAny]  # Geçici olarak herkesin erişimine açıyoruz

    def create(self, request, *args, **kwargs):
        # Aynı isimle form var mı kontrol et
        name = request.data.get('name')
        if EvaluationForm.objects.filter(name=name).exists():
            return Response(
                {'name': ['Bu isimle bir form zaten mevcut.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

class EvaluationViewSet(viewsets.ModelViewSet):
    """
    Değerlendirme işlemleri için API görünümü.
    """
    queryset = Evaluation.objects.all().order_by('-evaluated_at')
    permission_classes = [permissions.AllowAny]  # Geçici olarak herkesin erişimine açıyoruz

    def get_serializer_class(self):
        if self.action == 'create':
            return EvaluationCreateSerializer
        return EvaluationSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'is_admin') and (user.is_admin() or user.is_superuser):
            return Evaluation.objects.all().order_by('-evaluated_at')
        elif hasattr(user, 'is_expert') and user.is_expert():
            return Evaluation.objects.filter(evaluator=user).order_by('-evaluated_at')
        else:
            return Evaluation.objects.filter(call__agent=user).order_by('-evaluated_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Puan validasyonu
            form = serializer.validated_data['form']
            scores = serializer.validated_data['scores']
            
            for key, field in form.fields.items():
                max_score = field['max_score']
                if key in scores and scores[key]['score'] > max_score:
                    return Response(
                        {
                            'scores': [f'{key} için maksimum puan {max_score} olabilir.']
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            evaluation = serializer.save(evaluator=request.user)
            return Response(
                EvaluationSerializer(evaluation).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
