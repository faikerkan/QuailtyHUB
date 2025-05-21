from rest_framework import serializers
from accounts.models import CustomUser
from calls.models import CallRecord, Evaluation, EvaluationForm
from django.core.validators import FileExtensionValidator
from decimal import Decimal

class UserListSerializer(serializers.ModelSerializer):
    """
    Kullanıcı listesi için serializer
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'role', 'role_display', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']

class UserDetailSerializer(serializers.ModelSerializer):
    """
    Kullanıcı detayları için serializer
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'role', 'role_display', 'is_active', 'date_joined', 'last_login']
        read_only_fields = ['date_joined', 'last_login']

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Kullanıcı oluşturma için serializer
    """
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 
                  'role', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Şifreler eşleşmiyor."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Kullanıcı güncelleme için serializer
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']

class PasswordChangeSerializer(serializers.Serializer):
    """
    Şifre değiştirme için serializer
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Yeni şifreler eşleşmiyor."})
        return attrs 

class CallRecordSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.get_full_name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    call_queue_name = serializers.CharField(source='call_queue.name', read_only=True)
    audio_file = serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'm4a'])]
    )

    class Meta:
        model = CallRecord
        fields = [
            'id', 'uploaded_by', 'uploaded_by_name', 'agent', 'agent_name', 'call_queue', 'call_queue_name',
            'phone_number', 'audio_file', 'uploaded_at', 'call_date', 'call_id'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_by_name', 'uploaded_at']

class CallRecordUploadSerializer(serializers.ModelSerializer):
    audio_file = serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'm4a'])]
    )

    class Meta:
        model = CallRecord
        fields = [
            'agent', 'call_queue', 'phone_number', 'audio_file', 'call_date', 'call_id'
        ]

class EvaluationFormSerializer(serializers.ModelSerializer):
    """
    Değerlendirme formları için serileştirici.
    """
    class Meta:
        model = EvaluationForm
        fields = ['id', 'name', 'fields']

    def validate_fields(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("Alanlar listesi boş olamaz ve bir liste olmalıdır.")
        
        for field in value:
            if not all(k in field for k in ("key", "label", "type", "max_score")):
                raise serializers.ValidationError("Her alan 'key', 'label', 'type', 'max_score' içermelidir.")
            
            if not isinstance(field['max_score'], (int, float)) or field['max_score'] <= 0:
                raise serializers.ValidationError("max_score pozitif bir sayı olmalıdır.")
        
        return value

    def validate_name(self, value):
        # Aynı isimle form var mı kontrol et
        if EvaluationForm.objects.filter(name=value).exists():
            raise serializers.ValidationError("Bu isimle bir form zaten mevcut.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user if 'request' in self.context else None
        return EvaluationForm.objects.create(created_by=user, **validated_data)

class EvaluationSerializer(serializers.ModelSerializer):
    """
    Değerlendirme sonuçları için serileştirici.
    """
    evaluator_name = serializers.CharField(source='evaluator.get_full_name', read_only=True)
    call_id = serializers.IntegerField(source='call.id', read_only=True)
    form_name = serializers.CharField(source='form.name', read_only=True)
    total_score = serializers.FloatField(read_only=True)

    class Meta:
        model = Evaluation
        fields = [
            'id', 'call_id', 'evaluator', 'evaluator_name', 'form', 'form_name',
            'scores', 'final_note', 'evaluated_at', 'total_score'
        ]
        read_only_fields = ['id', 'evaluator', 'evaluator_name', 'evaluated_at', 'total_score']

class EvaluationCreateSerializer(serializers.ModelSerializer):
    """
    Yeni değerlendirme oluşturmak için serileştirici.
    """
    class Meta:
        model = Evaluation
        fields = ['call', 'form', 'scores', 'final_note']

    def validate_scores(self, value):
        form = self.initial_data.get('form')
        if not form:
            return value

        form_instance = EvaluationForm.objects.get(id=form)
        for field in form_instance.fields:
            key = field['key']
            max_score = field['max_score']
            if key in value and value[key] > max_score:
                raise serializers.ValidationError(f"{key} için maksimum puan {max_score} olabilir.")
        return value

    def create(self, validated_data):
        # Toplam puanı hesapla
        scores = validated_data.get('scores', {})
        form = validated_data.get('form')
        total_points = Decimal('0')
        max_points = Decimal('0')

        if form and hasattr(form, 'fields'):
            for field in form.fields:
                key = field.get('key')
                max_score = Decimal(str(field.get('max_score', 0)))
                value = Decimal(str(scores.get(key, 0)))
                total_points += value
                max_points += max_score

        if max_points > 0:
            total_score = (total_points / max_points) * Decimal('100')
            total_score = total_score.quantize(Decimal('0.01'))  # İki ondalık basamağa yuvarla
        else:
            total_score = Decimal('0')

        evaluation = Evaluation.objects.create(
            **validated_data,
            total_score=total_score
        )
        return evaluation 