from django.db import models
from django.utils import timezone

# Property Manager model
class Property_Manager(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, default='default@example.com')  # Ensure that the email is unique
    phone = models.CharField(max_length=15, null=True)  

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Tenant model (for linking tenants to a property manager)
class Tenant(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    property_manager = models.ForeignKey(Property_Manager, related_name='tenants', on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name

# Maintenance request model for tenants
class MaintenanceRequest(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField(default=timezone.now)
    availability = models.CharField(max_length=255, blank=True, null=True)
    request_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=50, default='Pending')
    contractor_name = models.CharField(max_length=255, blank=True, null=True)  # New field for contractor name
    contractor_message = models.TextField(null=True, blank=True) 
    contractor_phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Add the property_manager field to link to the Property_Manager model
    property_manager = models.ForeignKey(Property_Manager, related_name='maintenance_requests', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Request {self.request_number} by {self.full_name}"

# Image model for maintenance requests
class Image(models.Model):
    maintenance_request = models.ForeignKey(MaintenanceRequest, related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    file = models.ImageField(upload_to='maintenance_images/')
    created_at = models.DateTimeField(auto_now_add=True)
