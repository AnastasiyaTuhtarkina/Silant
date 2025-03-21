from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
    

class ServiceOrganization(models.Model):
    user = models.OneToOneField(
    User, 
    on_delete=models.CASCADE, 
    null=True,  # Разрешаем NULL в базе данных
    blank=True  # Разрешаем пустое значение в формах
)
    name = models.CharField(max_length=255, verbose_name='Название компании')
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})" if self.user else self.name
    
    class Meta:
        verbose_name = 'Сервисная компания'
        verbose_name_plural = 'Сервисные компании'
    

class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username 
    
    class Meta:
        verbose_name = 'Менеджер'
        verbose_name_plural = 'Менеджеры'

class Entity(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Уникальное имя сущности

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Сущность"
        verbose_name_plural = "Сущности"     
    

class Reference(models.Model):
    # Название сущности (название справочника)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='references', null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # Описание может быть пустым

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Справочник"
        verbose_name_plural = "Справочники"
        unique_together = ('entity', 'name')  # Уникальная комбинация сущности и названия          


class Machine(models.Model):
    serial_number = models.CharField(max_length=255, unique=True, verbose_name='Зав.№ машины')  # Зав. № машины
    model = models.ForeignKey(Reference, on_delete=models.SET_NULL, null=True, related_name='machines_model', verbose_name='Модель техники')
    engine_model = models.ForeignKey(Reference, on_delete=models.SET_NULL, null=True, related_name='engines_model', verbose_name='Модель двигателя')
    engine_serial_number = models.CharField(max_length=255, verbose_name='Зав.№ двигателя')
    transmission_model = models.ForeignKey(Reference, on_delete=models.SET_NULL, null=True, related_name='transmissions_model', verbose_name='Модель трансиссии(производитель, артикул)')
    transmission_serial_number = models.CharField(max_length=255, verbose_name='Зав.№ трансмиссии')
    axle_model = models.ForeignKey(Reference, on_delete=models.SET_NULL, null=True, related_name='axles_model', verbose_name='Модель ведущего моста')
    axle_serial_number = models.CharField(max_length=255, verbose_name='Зав.№ ведущего моста')
    steering_axle_model = models.ForeignKey(Reference, on_delete=models.SET_NULL, null=True, related_name='steering_axles_model', verbose_name='Модель управляемого моста')
    steering_axle_serial_number = models.CharField(max_length=255, verbose_name='Зав.№ управляемого моста')
    contract_number_data = models.CharField(max_length=255, verbose_name='Договор поставки №, дата')
    shipment_date = models.DateField(verbose_name='Дата отгрузки с завода')
    recipient = models.CharField(max_length=255, verbose_name='Грузополучатель (конечный потребитель)')
    delivery_address = models.CharField(max_length=255, verbose_name='Адрес поставки (эксплуатации)')
    configuration = models.TextField(verbose_name='Комплектация (доп.опции)')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name='machine', verbose_name='Клиент')
    service_company = models.ForeignKey(ServiceOrganization, on_delete=models.SET_NULL, null=True, related_name='machine', verbose_name='Сервисная компания')
    
    def __str__(self):
        return f"{self.serial_number} - {self.model.name}"
    
    class Meta:
        verbose_name = 'Машина'
        verbose_name_plural = 'Машины'


class TechnicalMaintenance(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.SET_NULL, null=True, related_name='maintenance', verbose_name='Машина')
    service_type = models.ForeignKey(Reference, on_delete=models.SET_NULL, null=True, related_name='maintenance_types', verbose_name='Вид ТО')
    maintenance_date = models.DateField(verbose_name='Дата проведения ТО')
    operating_hours = models.FloatField(verbose_name='Наработка, м/час')
    order_number = models.CharField(max_length=20, verbose_name='№ заказ-наряда')
    order_date = models.DateField(verbose_name='Дата заказ-наряда')
    content_type = models.ForeignKey(ServiceOrganization, on_delete=models.CASCADE, null=True, related_name='content_type', verbose_name='Организация, проводившая ТО')
    service_organization = models.ForeignKey(ServiceOrganization, on_delete=models.SET_NULL, null=True, related_name='performing_services', verbose_name='Сервисная организация')
    
    def __str__(self):
        return f"{self.service_type.name} for {self.machine.serial_number} on {self.maintenance_date}"
    
    class Meta:
        verbose_name = "Тех.обслуживание"
        verbose_name_plural = "Тех.обслуживание"


class Claim(models.Model):
    rejection_date = models.DateField(verbose_name='Дата отказа')
    operating_hours = models.FloatField(verbose_name='Наработка, м/час')
    failure_node = models.ForeignKey(Reference, on_delete=models.SET_NULL, null=True, related_name='failure_nodes', verbose_name='Узел отказа')
    failure_description = models.TextField(verbose_name='Описание отказа')
    recovery_method = models.ForeignKey(Reference, on_delete=models.SET_NULL, null=True, related_name='recovery_methods', verbose_name='Способ восстановления')
    used_spare_parts = models.TextField(verbose_name='Используемые запасные части')
    recovery_date = models.DateField(null=True, blank=True, verbose_name='Дата восстановления')
    downtime_duration = models.DurationField(blank=True, null=True, verbose_name='Время простоя техники')
    
    machine = models.ForeignKey(Machine, on_delete=models.SET_NULL, null=True, related_name='claim', verbose_name='Машина')
    service_company = models.ForeignKey(ServiceOrganization, on_delete=models.SET_NULL, null=True, related_name='claim', verbose_name='Сервисная компания')

    def save(self, *args, **kwargs):
        # Автоматический расчет времени простоя в начале сохранения
        if self.recovery_date and self.rejection_date:
            downtime = self.recovery_date - self.rejection_date
            self.downtime_duration = downtime
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Claim for {self.machine.serial_number} - Rejection Date: {self.rejection_date}'

    class Meta:
        verbose_name = "Рекламация"
        verbose_name_plural = "Рекламации"

class AuthForm(forms.Form):
    organization = forms.CharField(max_length=255, label='Наименование организации')
    status = forms.CharField(max_length=255, label='Статус')



