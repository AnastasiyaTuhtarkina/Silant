from rest_framework import serializers

from .models import Machine

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        if not user.is_authenticated:
            # Ограничиваем поля для неавторизованных пользователей
            allowed_fields = ['serial_number', 'model', 'engine_model', 'transmission_model', 'axle_model', 'steering_axle_model', 'shipment_date']
            return {field: data[field] for field in allowed_fields}
        return data