from rest_framework import serializers
from .models import MaintenanceRequest, Property_Manager, Image, Unit, Tenant, Notification
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
import json


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required = True, write_only = True)
    access_token = serializers.CharField(read_only = True)
    refresh_token = serializers.CharField(read_only = True)

    class Meta:
        model = Property_Manager
        fields = ['first_name','last_name','email','password','confirm_password','access_token','refresh_token']
        extra_kwargs = {
            'email' : {'validators': [UniqueValidator(queryset = Property_Manager.objects.all(),message  ="Email is already registered")]},
            'password': {'write_only': True}
        }

    def validate(self,data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError({"error":"Passwords do not match"})
        
        data.pop('confirm_password')
        return data

    def create(self,validated_data):
        user = self.Meta.model.objects.create_user(**validated_data)
        return user

class RegisterUnitSerializer(serializers.ModelSerializer):
    primary_tenant_name = serializers.CharField(max_length=255)
    primary_tenant_email = serializers.EmailField()

    class Meta:
        model = Unit
        fields = ['id','title', 'address', 'notes', 'primary_tenant_name', 'primary_tenant_email']
        extra_kwargs = {
            'id': {'read_only':True},
            'primary_tenant_email' : {'validators': [UniqueValidator(queryset = Tenant.objects.all(),message  ="Email is already registered")]},
        }

    def save(self,**kwargs):
        data = self.validated_data
        # Create Tenant
        full_name = data.get('primary_tenant_name')
        email = data.get('primary_tenant_email')
        tenant = Tenant.objects.create(full_name=full_name,email=email)
        # Create Unit
        property_manager = self.context.get('user')
        title = data.get('title')
        address = data.get('address')
        notes = data.get('notes')
        unit = Unit.objects.create(title=title, address=address, notes=notes,property_manager=property_manager,tenant=tenant)
        return {**data,"id":unit.id}

class LoginSerializer(serializers.Serializer):
    # FIELDS FOR AUTHENTICATION
    email = serializers.EmailField(required = True)
    password = serializers.CharField(required = True, write_only = True)
    # EXTRA FIELDS RETURNED IN RESPONSE
    id = serializers.IntegerField(read_only = True)
    first_name = serializers.CharField(read_only = True)
    last_name = serializers.CharField(read_only = True)
    access_token = serializers.CharField(read_only = True)
    refresh_token = serializers.CharField(read_only = True)

    def validate(self,data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(username = email, password = password)
        if not user:
            raise serializers.ValidationError({"error": "Invalid credentials"})
        else:
            return {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'access_token': user.access_token,
                'refresh_token': user.refresh_token
            }

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    isClosed = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceRequest
        fields = ['id','subject','status','priority','updated_at','unit','isClosed']

    def get_isClosed(self, obj):
        return obj.status == 'Request Complete'

    def to_representation(self,instance):
        representation = super().to_representation(instance)
        representation['unit'] = {"id": instance.unit.id,"address":instance.unit.address}
        return representation

class NewMaintenanceRequestSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required = False)
    email = serializers.EmailField(required = False)
    images = serializers.ListField(
        child=serializers.ImageField(write_only=True), write_only=True, required=False
    )

    class Meta:
        model = MaintenanceRequest
        fields = ['full_name','email','unit','subject','property_manager_message','availability','priority','status','contractor_name','contractor_phone']

    def create(self, validated_data):
        validated_data['full_name'] = validated_data.get('unit').tenant.full_name
        validated_data['email'] = validated_data.get('unit').tenant.email
        validated_data['property_manager'] = self.context.get('user')
        images = validated_data.pop('images')
        instance = self.Meta.model.objects.create(**validated_data)
        for image in images:
            Image.objects.create(uploded_by="property_manager",maintenance_request = instance, file = image)
        return instance

    #     {
    #   id: 1,
    #   title: "Leak in the ceiling",
    #   unit: "123 Main St, unit 100",
    #   status: "Called Contractor",
    #   priority: "high",
    #   updatedAt: "2023-08-29",
    #   color: "#DC3545BF", // High priority (red)
    #   isClosed: false,
    # },
    class Meta:
        model = MaintenanceRequest
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
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

    def update(self, instance, validated_data):
        # Update Tenant
        tenant = validated_data.pop('tenant', None)
        if tenant:
            instance.tenant.full_name = tenant.get('full_name',instance.tenant.full_name)
            instance.tenant.email = tenant.get('email',instance.tenant.email)
            instance.tenant.save()
        # Update the Unit fields
        instance.title = validated_data.get('title', instance.title)
        instance.address = validated_data.get('address', instance.address)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()
        # Return Instance
        return instance

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'
        
class NotificationSerializer(serializers.ModelSerializer):
    unit_title = serializers.CharField(source='tenant.unit.title')
    issue = serializers.CharField(source = 'maintenance_request.subject')

    class Meta:
        model = Notification
        fields = ['id', 'issue', 'unit_title','maintenance_request'] 
        # fields = '__all__'

class RequestDetailSerializer(serializers.ModelSerializer):
    unit_title = serializers.CharField(source='unit.title')
    unit_address = serializers.CharField(source='unit.address')
    tenant_email = serializers.CharField(source='unit.tenant.email')
    notes = serializers.CharField(source='unit.notes')
    tenant_images = serializers.SerializerMethodField()
    property_manager_images = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceRequest
        fields = ['id','unit_title', 'unit_address', 'tenant_email','notes','subject','tenant_message','property_manager_message','availability','status','priority','contractor_name','contractor_phone','tenant_images','property_manager_images']

    def get_tenant_images(self, obj):
        # Filter images by task ID and uploader_type 'student'
        tenant_images = Image.objects.filter(maintenance_request=obj.id, uploded_by='tenant')
        return ImageSerializer(tenant_images, many=True).data

    def get_property_manager_images(self, obj):
        property_manager_images = Image.objects.filter(maintenance_request=obj.id, uploded_by='property_manager')
        return ImageSerializer(property_manager_images, many=True).data

class RequestUpdateSerializer(serializers.ModelSerializer):
    new_files = serializers.ListField(
        child=serializers.FileField(), required=False, allow_empty=True
    )
    deleted_files = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )

    def validate_deleted_files(self, value):
        try:
            value = json.loads(value[0])
            value = [int(item) for item in value]
        except ValueError:
            raise serializers.ValidationError("All items in deleted_files must be valid integers.")
        
        return value

    class Meta:
        model = MaintenanceRequest
        fields = ['property_manager_message','status','priority','contractor_name','contractor_phone','new_files','deleted_files'] 

    def update(self, instance, validated_data):
        # Update Tenant
        tenant = validated_data.pop('tenant', None)
        if tenant:
            instance.tenant.full_name = tenant.get('full_name',instance.tenant.full_name)
            instance.tenant.email = tenant.get('email',instance.tenant.email)
            instance.tenant.save()
        # Handle new files
        new_images = validated_data.pop('new_files',[])
        for image in new_images:
            Image.objects.create(uploded_by="property_manager",maintenance_request = instance, file = image)
        # Handle deleted files
        deleted_images = validated_data.pop('deleted_files',[])
        if len(deleted_images):
            Image.objects.filter(id__in=deleted_images).delete()
        # Update the Unit fields
        instance.property_manager_message = validated_data.get('property_manager_message', instance.property_manager_message)
        instance.status = validated_data.get('status', instance.status)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.contractor_name = validated_data.get('contractor_name', instance.contractor_name)
        instance.contractor_phone = validated_data.get('contractor_phone', instance.contractor_phone)
        instance.save()
        # Return Instance
        return instance 