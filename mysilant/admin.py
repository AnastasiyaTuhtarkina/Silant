from django.contrib import admin
from django.core.cache import cache
from django_flatpickr.widgets import DatePickerInput
from django_flatpickr.schemas import FlatpickrOptions

from .models import *


admin.site.register(Client)
admin.site.register(Manager)


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ['entity', 'name']
    search_fields = ['name']

@admin.register(ServiceOrganization)
class ServiceOrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'description')
    search_fields = ('name', 'user__username')
    list_filter = ('name',)

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'model', 'engine_model', 'transmission_model', 'axle_model', 'steering_axle_model')
    list_filter = ('model', 'engine_model', 'transmission_model', 'axle_model', 'steering_axle_model')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Словарь для связи полей модели Machine с entity_name справочников
        reference_fields = {
            'model': 'Модель техники',
            'engine_model': 'Модель двигателя',
            'transmission_model': 'Модель трансмиссии',
            'axle_model': 'Модель ведущего моста',
            'steering_axle_model': 'Модель управляемого моста',
        }

        # Динамически фильтруем справочники для каждого поля
        if db_field.name in reference_fields:
            entity_name = reference_fields[db_field.name]
            safe_entity_name = entity_name.replace(':', '_')
            safe_db_field_name = db_field.name.replace(':', '_')

            cache_key = f'reference_queryset_{safe_entity_name}_{safe_db_field_name}'  # Уникальный ключ

            # Пытаемся получить данные из кэша
            queryset = cache.get(cache_key)
            if not queryset:
                try:
                    entity = Entity.objects.get(name=entity_name)
                    queryset = Reference.objects.filter(entity=entity)
                    cache.set(cache_key, queryset, timeout=60 * 60)  # Кэшируем на 1 час
                except Entity.DoesNotExist:
                    queryset = Reference.objects.none()

            kwargs["queryset"] = queryset

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'shipment_date':  # Замените на имя вашего поля
            flatpickr_options = FlatpickrOptions(
                altFormat="d-m-Y",  # Формат даты
                maxDate="today",    # Максимальная дата — сегодня
                locale="ru",        # Русская локализация
            )

            kwargs['widget'] = DatePickerInput(
                attrs={
                    'class': 'my-custom-class',  # CSS-класс
                },
                options=flatpickr_options
            )
        return super().formfield_for_dbfield(db_field, **kwargs)

    class Media:
        css = {
            'all': ('css/flatpickr_custom.css',)  # Подключение кастомных стилей
        }
        js = [
            'https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/ru.js',  # Русская локализация
        ]

@admin.register(TechnicalMaintenance)
class TechMaintAdmin(admin.ModelAdmin):
    list_display = ('machine', 'service_type', 'maintenance_date', 'operating_hours', 'order_number', 'order_date')  # Кортеж с одним элементом
    list_filter = ('service_type', 'machine')   # Кортеж с одним элементом

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Словарь для связи полей модели Machine с entity_name справочников
        reference_fields = {
            'service_type': 'Вид ТО',
        }

        # Динамически фильтруем справочники для каждого поля
        if db_field.name in reference_fields:
            entity_name = reference_fields[db_field.name]
            safe_entity_name = entity_name.replace(':', '_')
            safe_db_field_name = db_field.name.replace(':', '_')

            cache_key = f'reference_queryset_{safe_entity_name}_{safe_db_field_name}'  # Уникальный ключ

            # Пытаемся получить данные из кэша
            queryset = cache.get(cache_key)
            if not queryset:
                try:
                    entity = Entity.objects.get(name=entity_name)
                    queryset = Reference.objects.filter(entity=entity)
                    cache.set(cache_key, queryset, timeout=60 * 60)  # Кэшируем на 1 час
                except Entity.DoesNotExist:
                    queryset = Reference.objects.none()
                    # Логирование или уведомление об ошибке
                    print(f"Entity with name '{entity_name}' does not exist.")

            kwargs["queryset"] = queryset

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['maintenance_date', 'order_date']:
            flatpickr_options = FlatpickrOptions(
                altFormat="d-m-Y",  # Формат даты
                maxDate="today",    # Максимальная дата — сегодня
                locale="ru",        # Русская локализация
            )

            kwargs['widget'] = DatePickerInput(
                attrs={
                    'class': 'my-custom-class',  # CSS-класс
                },
                options=flatpickr_options
            )
        return super().formfield_for_dbfield(db_field, **kwargs)

    class Media:
        css = {
            'all': ('css/flatpickr_custom.css',)  # Подключение кастомных стилей
        }
        js = [
            'https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/ru.js',  # Русская локализация
        ]

    
@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('machine', 'rejection_date', 'operating_hours', 'failure_node', 'recovery_method', 'recovery_date')  # Кортеж с одним элементом

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Словарь для связи полей модели Machine с entity_name справочников
        reference_fields = {
            'failure_node': 'Узел отказа',
            'recovery_method': 'Способ восстановления',
        }

        # Динамически фильтруем справочники для каждого поля
        if db_field.name in reference_fields:
            entity_name = reference_fields[db_field.name]
            safe_entity_name = entity_name.replace(':', '_')
            safe_db_field_name = db_field.name.replace(':', '_')

            cache_key = f'reference_queryset_{safe_entity_name}_{safe_db_field_name}'  # Уникальный ключ

            # Пытаемся получить данные из кэша
            queryset = cache.get(cache_key)
            if not queryset:
                try:
                    entity = Entity.objects.get(name=entity_name)
                    queryset = Reference.objects.filter(entity=entity)
                    cache.set(cache_key, queryset, timeout=60 * 60)  # Кэшируем на 1 час
                except Entity.DoesNotExist:
                    queryset = Reference.objects.none()
                    # Логирование или уведомление об ошибке
                    print(f"Entity with name '{entity_name}' does not exist.")

            kwargs["queryset"] = queryset

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['rejection_date', 'recovery_date']: 
            flatpickr_options = FlatpickrOptions(
                altFormat="d-m-Y",  # Формат даты
                maxDate="today",    # Максимальная дата — сегодня
                locale="ru",        # Русская локализация
            )

            kwargs['widget'] = DatePickerInput(
                attrs={
                    'class': 'my-custom-class',  # CSS-класс
                },
                options=flatpickr_options
            )
        return super().formfield_for_dbfield(db_field, **kwargs)

    class Media:
        css = {
            'all': ('css/flatpickr_custom.css',)  # Подключение кастомных стилей
        }
        js = [
            'https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/ru.js',  # Русская локализация
        ]