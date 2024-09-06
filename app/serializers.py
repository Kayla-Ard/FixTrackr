from rest_framework import serializers
from .models import MaintenanceRequest, Property_Manager, Image, Unit, Tenant, Notification

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
        
class UnitSerializer(serializers.ModelSerializer):
    tenant_full_name = serializers.CharField(source='tenant.full_name')
    tenant_email = serializers.EmailField(source='tenant.email')
    class Meta:
        model = Unit
        fields = ['id', 'title', 'address', 'tenant_full_name', 'tenant_email', 'notes']

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'
        
class NotificationSerializer(serializers.ModelSerializer):
    unit_title = serializers.CharField(source='tenant.unit.title', read_only=True)  # Assuming tenant has a unit

    class Meta:
        model = Notification
        # fields = ['id', 'message', 'unit_title', 'created_at'] 
        fields = '__all__'