from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Reference, Entity, TechnicalMaintenance, Claim

class EntityForm(forms.ModelForm):
    class Meta:
        model = Entity
        fields = ['name']

class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference
        fields = ['entity', 'name', 'description']

class RegForm(forms.Form):
    organization = forms.CharField(max_length=100, label="Наименование организации")
    STATUS_CHOICES = [
        ('client', 'Клиент'),
        ('service', 'Сервисная организация'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, label="Выберите статус") 

class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', max_length=150)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = TechnicalMaintenance
        fields = [
            'machine',
            'service_type',
            'maintenance_date',
            'operating_hours',
            'order_number',
            'order_date',
            'content_type',
            'service_organization'
        ]
        widgets = {
            'maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'order_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = [
            'rejection_date',
            'operating_hours',
            'failure_node',
            'failure_description',
            'recovery_method',
            'used_spare_parts',
            'recovery_date',
            'downtime_duration',
            'machine',
            'service_company'
        ]
        widgets = {
            'rejection_date': forms.DateInput(attrs={'type': 'date'}),
            'recovery_date': forms.DateInput(attrs={'type': 'date'}),
        }       