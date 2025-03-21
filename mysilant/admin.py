from django.contrib import admin
from .models import *


admin.site.register(Client)
admin.site.register(Manager)
admin.site.register(TechnicalMaintenance)
admin.site.register(Claim)


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
            # Находим нужный entity по названию
            entity_name = reference_fields[db_field.name]
            try:
                entity = Entity.objects.get(name=entity_name)  # Находим Entity с соответствующим name
                kwargs["queryset"] = Reference.objects.filter(entity=entity)
            except Entity.DoesNotExist:
                kwargs["queryset"] = Reference.objects.none()  # Если entity не найден, не показывать записи

        return super().formfield_for_foreignkey(db_field, request, **kwargs)