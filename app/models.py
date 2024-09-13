from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import serializers
import datetime
from .managers import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

# Property Manager model
class Property_Manager(AbstractBaseUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_superuser = models.BooleanField(default = False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @property
    def access_token(self):
        token = AccessToken.for_user(self)
        return str(token)

    @property
    def refresh_token(self):
        token = RefreshToken.for_user(self)
        return str(token)

# Tenant model (for linking tenants to a property manager)
class Tenant(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    # property_manager = models.ForeignKey(Property_Manager, related_name='tenants', on_delete=models.CASCADE)
    # unit = models.ForeignKey('Unit', related_name='tenant', on_delete=models.CASCADE, null=True, blank=True)  

    def __str__(self):
        return self.full_name
    
# Unit models
class Unit(models.Model):
    title = models.CharField(max_length=255)
    address = models.TextField()
    notes = models.TextField(blank=True, null=True)
    tenant = models.OneToOneField(Tenant, related_name = "unit", on_delete=models.CASCADE)
    property_manager = models.ForeignKey(Property_Manager, related_name='units', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.address}"
    
# Tenant model (for linking tenants to a property manager)
# class Tenant(models.Model):
#     full_name = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     property_manager = models.ForeignKey(Property_Manager, related_name='tenants', on_delete=models.CASCADE)
#     unit = models.ForeignKey(Unit, related_name='tenants', on_delete=models.CASCADE, null=True, blank=True)  

#     def __str__(self):
#         return self.full_name

# Maintenance request model for tenants
class MaintenanceRequest(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'low'),
        ('high', 'high'),
    ]

    STATUS_CHOICES = [
        ('Pending','Pending'),
        ('Request Sent', 'Request Sent'),
        ('Request Read', 'Request Read'),
        ('Contractor Called', 'Contractor Called'),
        ('Appointment Set', 'Appointment Set'),
        ('Request Complete', 'Request Complete'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    property_manager_message = models.TextField(null=True, blank=True)
    tenant_message = models.TextField(null=True, blank=True)
    date_sent = models.DateTimeField(default=timezone.now)
    availability = models.CharField(max_length=255, blank=True, null=True)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='Low Priority')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Request Sent')
    contractor_name = models.CharField(max_length=255, blank=True, null=True)
    contractor_phone = models.CharField(max_length=15, blank=True, null=True)
    request_date = models.DateField(default=datetime.date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unit = models.ForeignKey(Unit, related_name='maintenance_requests', on_delete=models.CASCADE, null=True, blank=True)
    property_manager = models.ForeignKey(Property_Manager, related_name='maintenance_requests', on_delete=models.CASCADE, null=True, blank=True)
    request_number = models.CharField(max_length=100, null=True, blank=True)

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
    
    def __str__(self):
        return f"Request by {self.full_name}"

# Image model for maintenance requests
class Image(models.Model):
    UPLOADER_CHOICES = [
        ('tenant', 'tenant'),
        ('property_manager', 'property_manager'),
    ]

    uploded_by = models.CharField(max_length=16, choices=UPLOADER_CHOICES, default='tenant')
    maintenance_request = models.ForeignKey(MaintenanceRequest, related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    file = models.ImageField(upload_to='maintenance_images/')
    created_at = models.DateTimeField(auto_now_add=True)

# Notification model for property managers
class Notification(models.Model):
    property_manager = models.ForeignKey(Property_Manager, related_name='notifications', on_delete=models.CASCADE)
    maintenance_request = models.ForeignKey(MaintenanceRequest, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Notification for {self.property_manager.first_name} {self.property_manager.last_name}"