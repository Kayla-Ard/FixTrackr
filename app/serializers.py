from rest_framework import serializers
from .models import MaintenanceRequest, Property_Manager

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRequest
        fields = '__all__'

class PropertyManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property_Manager
        fields = '__all__'