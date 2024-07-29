from django.contrib import admin
from .models import Property_Manager

# This is where we register our models(tables)

# Creating a Property Manager Admin class and specifying fields in a list_display for easier visualization on admin site
class Property_Manager_Admin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone',)

# Registering the Property Manager class from models.py
admin.site.register(Property_Manager, Property_Manager_Admin)