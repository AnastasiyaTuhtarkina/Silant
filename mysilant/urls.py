from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('auth/', auth_view, name='auth_view'),
    path('reg/', reg_view, name='reg_view'),
    path('success/', success_view, name='success'),
    path('logout/', custom_logout, name='logout'),
    path('machine_detail/<int:machine_id>/', machine_detail, name='machine_detail'),
    path('add_machine/', add_machine, name='add_machine'),
    path('add-reference/', add_reference, name='add_reference'),
    path('add_maintenance/', add_maintenance, name='add_maintenance'),
    path('add_claim/', add_claim, name='add_claim'),
    path('api/', api_page, name='api-page'),
    path('api/machines/', MachineList.as_view(), name='machine-list'),
    path('api/maintenances/', MaintenanceList.as_view(), name='maintenance-list'),
    path('api/claims/', ClaimList.as_view(), name='claim-list'),
]
