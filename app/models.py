from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import serializers
import datetime

# Property Manager model
class Property_Manager(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE) 
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, default='default@example.com')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Tenant model (for linking tenants to a property manager)
class Tenant(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    property_manager = models.ForeignKey(Property_Manager, related_name='tenants', on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name

# Unit models
class Unit(models.Model):
    title = models.CharField(max_length=255)
    address = models.TextField()
    notes = models.TextField(blank=True, null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    property_manager = models.ForeignKey(Property_Manager, related_name='units', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.address}"
    


# Maintenance request model for tenants
class MaintenanceRequest(models.Model):
    PRIORITY_CHOICES = [
        ('Low Priority', 'Low Priority'),
        ('High Priority', 'High Priority'),
    ]

    STATUS_CHOICES = [
        ('Request Sent', 'Request Sent'),
        ('Request Read', 'Request Read'),
        ('Contractor Called', 'Contractor Called'),
        ('Appointment Set', 'Appointment Set'),
        ('Request Complete', 'Request Complete'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField(default=timezone.now)
    availability = models.CharField(max_length=255, blank=True, null=True)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='Low Priority')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Request Sent')
    contractor_name = models.CharField(max_length=255, blank=True, null=True)
    property_manager_message = models.TextField(null=True, blank=True)
    contractor_phone = models.CharField(max_length=15, blank=True, null=True)
    request_date = models.DateField(default=datetime.date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    unit = models.ForeignKey(Unit, related_name='maintenance_requests', on_delete=models.CASCADE, null=True, blank=True)
    property_manager = models.ForeignKey(Property_Manager, related_name='maintenance_requests', on_delete=models.CASCADE, null=True, blank=True)
    request_number = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"Request by {self.full_name}"

# Image model for maintenance requests
class Image(models.Model):
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

    def __str__(self):
        return f"Notification for {self.property_manager.first_name} {self.property_manager.last_name}"