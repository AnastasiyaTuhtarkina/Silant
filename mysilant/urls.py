from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('auth/', auth_view, name='auth_view'),
    path('reg/', reg_view, name='reg_view'),
    path('success/', success_view, name='success'),
    path('claims/', ClaimUpdateView, name='claims_view'),
    path('technical_maintenances/', TechnicalMaintenanceUpdateView, name='technical_maintenances_update'),
    path('machine_list/', MachineUpdateView, name='machine_list'),
]