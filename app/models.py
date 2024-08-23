from django.db import models
from django.utils import timezone

# We create our models(tables) here.

# For when the property manager is registering 
class Property_Manager(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  # Ensure that the email is unique
    phone = models.CharField(max_length=15, null=True)  

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# For when the property manager is registering the tenant - connects them with email 
class Tenant(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    property_manager = models.ForeignKey(Property_Manager, related_name='tenants', on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name

    
# Maintenance request form on the tenant website 
class MaintenanceRequest(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField(default=timezone.now)
    availability = models.CharField(max_length=255, blank=True, null=True)
    request_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Image(models.Model):
    maintenance_request = models.ForeignKey(MaintenanceRequest, related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    file = models.ImageField(upload_to='maintenance_images/')
    created_at = models.DateTimeField(auto_now_add=True)