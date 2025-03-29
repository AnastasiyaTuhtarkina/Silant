from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('auth/', auth_view, name='auth_view'),
    path('reg/', reg_view, name='reg_view'),
    path('success/', success_view, name='success'),
    path('logout/', custom_logout, name='logout'),
    path('claims/', ClaimUpdateView.as_view(), name='claims_view'),
    path('machine_list/', MachineUpdateView.as_view(), name='machine_list'),
    path('technical_maintenances/', TechnicalMaintenanceUpdateView.as_view(), name='technical_maintenances_update'),
    path('machine_detail/<int:machine_id>/', machine_detail, name='machine_detail'),
]