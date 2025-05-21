from django import forms
from django.contrib.auth import get_user_model
from .models import EvaluationForm, CallRecord, Evaluation, CallQueue

User = get_user_model()

class CallRecordForm(forms.ModelForm):
    """
    Çağrı kaydı yükleme formu
    """
    class Meta:
        model = CallRecord
        fields = ['agent', 'call_queue', 'phone_number', 'call_date', 'audio_file']
        widgets = {
            'agent': forms.Select(attrs={'class': 'form-control'}),
            'call_queue': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '05XX XXX XX XX'}),
            'call_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'audio_file': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Sadece müşteri temsilcisi rolüne sahip kullanıcıları göster
        self.fields['agent'].queryset = User.objects.filter(role='agent')

class EvaluationCreateForm(forms.ModelForm):
    """
    Değerlendirme oluşturma formu
    """
    final_note = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        label="Değerlendirme Notu",
        required=True
    )
    
    class Meta:
        model = Evaluation
        fields = ['final_note']
    
    def __init__(self, *args, **kwargs):
        self.form_template = kwargs.pop('form_template', None)
        super().__init__(*args, **kwargs)
        
        # Dinamik form alanlarını ekle
        if self.form_template:
            form_fields = self.form_template.fields
            for field_id, field_data in form_fields.items():
                field_type = field_data.get('type', 'number')
                field_label = field_data.get('label', f'Alan {field_id}')
                field_max = field_data.get('max_score', 10)
                
                if field_type == 'number':
                    self.fields[f'score_{field_id}'] = forms.IntegerField(
                        label=field_label,
                        min_value=0,
                        max_value=field_max,
                        widget=forms.NumberInput(attrs={
                            'class': 'form-control',
                            'data-field-id': field_id,
                            'data-max-score': field_max
                        })
                    )
                elif field_type == 'boolean':
                    self.fields[f'score_{field_id}'] = forms.ChoiceField(
                        label=field_label,
                        choices=[(1, 'Evet'), (0, 'Hayır')],
                        widget=forms.RadioSelect(attrs={
                            'class': 'form-check-input',
                            'data-field-id': field_id
                        })
                    )
    
    def clean(self):
        cleaned_data = super().clean()
        # Form alanlarından scores JSON'ını oluştur
        scores = {}
        
        if self.form_template:
            form_fields = self.form_template.fields
            for field_id in form_fields.keys():
                score_key = f'score_{field_id}'
                if score_key in cleaned_data:
                    scores[field_id] = {
                        'score': cleaned_data[score_key],
                        'max_score': form_fields[field_id].get('max_score', 10),
                        'label': form_fields[field_id].get('label', f'Alan {field_id}')
                    }
        
        # scores alanını temizlenmiş veriye ekle
        cleaned_data['scores'] = scores
        
        # Toplam puanı hesapla
        total_points = sum(item['score'] for item in scores.values())
        max_points = sum(item['max_score'] for item in scores.values())
        
        if max_points > 0:
            total_score = (total_points / max_points) * 100
        else:
            total_score = 0
            
        cleaned_data['total_score'] = total_score
        
        return cleaned_data 