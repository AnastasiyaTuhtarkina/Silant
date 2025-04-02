from rest_framework import serializers

from .models import Machine, TechnicalMaintenance, Claim

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'  # Или укажите конкретные поля

class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalMaintenance
        fields = '__all__'  # Или укажите конкретные поля

class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = '__all__'  # Или укажите конкретные поля