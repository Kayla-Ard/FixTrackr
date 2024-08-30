from django.contrib import admin
from .models import Property_Manager, MaintenanceRequest, User

# This is where we register our models(tables)

@admin.register(Property_Manager)
class PropertyManagerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')
    search_fields = ('first_name', 'last_name', 'email')



@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('property_manager', 'request_date', 'status')
    search_fields = ('property_manager__first_name', 'property_manager__last_name', 'status')



# Registering the Maintenance Request class from models.py
# admin.site.register(MaintenanceRequest)