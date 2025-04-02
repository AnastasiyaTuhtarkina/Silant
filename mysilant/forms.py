from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy

from .models import Reference, Entity, TechnicalMaintenance, Claim, Machine

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

class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Словарь соответствия полей модели и названий сущностей
        field_to_entity = {
            'model': 'Модель техники',
            'engine_model': 'Модель двигателя',
            'transmission_model': 'Модель трансмиссии',
            'axle_model': 'Модель ведущего моста',
            'steering_axle_model': 'Модель управляемого моста'
        }
        
        for field_name, entity_name in field_to_entity.items():
            try:
                entity = Entity.objects.get(name=entity_name)
                self.fields[field_name].queryset = Reference.objects.filter(entity=entity)
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-control reference-select',
                    'data-entity': entity_name,
                    'data-url': reverse_lazy('add_reference')  # URL для добавления
                })
            except Entity.DoesNotExist:
                self.fields[field_name].queryset = Reference.objects.none()
                print(f"Сущность '{entity_name}' не найдена!")
        
        # Настройка других полей
        self.fields['shipment_date'].widget = forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'})

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = TechnicalMaintenance
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Словарь соответствия полей модели и названий сущностей
        field_to_entity = {
            'service_type': 'Вид ТО',
        }
        
        for field_name, entity_name in field_to_entity.items():
            try:
                entity = Entity.objects.get(name=entity_name)
                self.fields[field_name].queryset = Reference.objects.filter(entity=entity)
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-control reference-select',
                    'data-entity': entity_name,
                    'data-url': reverse_lazy('add_reference')  # URL для добавления
                })
            except Entity.DoesNotExist:
                self.fields[field_name].queryset = Reference.objects.none()
                print(f"Сущность '{entity_name}' не найдена!")
        
        # Настройка других полей
        self.fields['maintenance_date'].widget = forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
        })
        self.fields['order_date'].widget = forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
        })
        
class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Словарь соответствия полей модели и названий сущностей
        field_to_entity = {
            'failure_node': 'Узел отказа',
            'recovery_method': 'Способ восстановления',
        }
        
        for field_name, entity_name in field_to_entity.items():
            try:
                entity = Entity.objects.get(name=entity_name)
                self.fields[field_name].queryset = Reference.objects.filter(entity=entity)
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-control reference-select',
                    'data-entity': entity_name,
                    'data-url': reverse_lazy('add_reference')  # URL для добавления
                })
            except Entity.DoesNotExist:
                self.fields[field_name].queryset = Reference.objects.none()
                print(f"Сущность '{entity_name}' не найдена!")
        
        # Настройка других полей
        self.fields['rejection_date'].widget = forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
        })

        self.fields['recovery_date'].widget = forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
        })

        def save(self, commit=True):
            # Сначала сохраняем объект
            claim = super().save(commit=False)

            # Здесь вы можете добавить дополнительную логику, если необходимо
            # Например, вы можете автоматически рассчитывать время простоя
            if claim.recovery_date and claim.rejection_date:
                downtime = claim.recovery_date - claim.rejection_date
                claim.downtime_duration = downtime  # Предполагается, что поле downtime_duration существует в модели

            # Сохраняем объект в базе данных
            if commit:
                claim.save()

            return claim


