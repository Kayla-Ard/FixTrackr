from django.db import models
from django.utils import timezone

# We create our models(tables) here.

class Property_Manager(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(null=True)
    phone = models.IntegerField(null=True)
    
    

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