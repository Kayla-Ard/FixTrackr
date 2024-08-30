from rest_framework import serializers
from .models import MaintenanceRequest, Property_Manager, Image, Unit

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['file']

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)  

    class Meta:
        model = MaintenanceRequest
        fields = '__all__'

class PropertyManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property_Manager
        fields = '__all__'