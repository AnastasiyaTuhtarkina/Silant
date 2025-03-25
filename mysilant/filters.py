import django_filters
from .models import Machine, TechnicalMaintenance, Claim

class MachineFilter(django_filters.FilterSet):

    # Фильтрация по связанным объектам
    model = django_filters.CharFilter(field_name='model__name', lookup_expr='icontains', label='Модель техники')
    engine_model = django_filters.CharFilter(field_name='engine_model__name', lookup_expr='icontains', label='Модель двигателя')
    transmission_model = django_filters.CharFilter(field_name='transmission_model__name', lookup_expr='icontains', label='Модель трансмиссии')
    axle_model = django_filters.CharFilter(field_name='axle_model__name', lookup_expr='icontains', label='Модель ведущего моста')
    steering_axle_model = django_filters.CharFilter(field_name='steering_axle_model__name', lookup_expr='icontains', label='Модель управляемого моста')
    client = django_filters.CharFilter(field_name='client__name', lookup_expr='icontains', label='Клиент')
    service_company = django_filters.CharFilter(field_name='service_company__name', lookup_expr='icontains', label='Сервисная компания')

    class Meta:
        model = Machine
        fields = [
            'model',
            'engine_model',
            'transmission_model',
            'axle_model',
            'steering_axle_model',
        ]

class MaintenanceFilter(django_filters.FilterSet):
    service_type = django_filters.CharFilter(field_name='service_type', lookup_expr='icontains', label='Вид ТО')
    machine = django_filters.CharFilter(field_name='machine', lookup_expr='icontains', label='Зав.№ машины')
    service_organization = django_filters.CharFilter(field_name='service_organization', lookup_expr='icontains', label='Сервисная компания')

    class Meta:
        model = TechnicalMaintenance
        fields = [
            'service_type',
            'machine',
            'service_organization',
        ]

class ClaimFilter(django_filters.FilterSet):
    failure_node = django_filters.CharFilter(field_name='failure_node', lookup_expr='icontains', label='Узел отказа')
    recovery_method = django_filters.CharFilter(field_name='recovery_method', lookup_expr='icontains', label='Способ восстановления')
    service_company = django_filters.CharFilter(field_name='service_company', lookup_expr='icontains', label='Сервисная компания')
