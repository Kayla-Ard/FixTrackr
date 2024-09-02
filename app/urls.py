# This code snippet is defining URL patterns for a Django web application. Each `path` function call
# maps a URL pattern to a specific view function within the application. Here's a breakdown of what
# each part is doing:
# This code snippet is defining URL patterns for a Django web application. In Django, URL patterns are
# defined in the `urlpatterns` list within the `urls.py` file of an app. Each URL pattern is
# associated with a specific view function that will be called when a matching URL is accessed.
from django.urls import path
from . import views


urlpatterns = [
    
    # Tenant URLs
    path('', views.tenant_home, name='tenant_home'),
    path('submit-request/', views.submit_request, name='submit_request'),
    path('check-request-status/', views.check_request_status, name='check_request_status'),
    path('progress-check/', views.progress_check, name='progress_check_no_number'),
    path('progress-check/<str:request_number>/', views.progress_check, name='progress_check'), 
    path('request_submitted/', views.request_submitted, name='request_submitted.html'),
    
    # Property Manager API URLs
    path('api/register-property-manager/', views.register_property_manager, name='register_property_manager'),
    path('api/login/', views.login, name='login'),
    
    # Unit management URLs
    path('api/units/', views.list_units, name='list_units'),
    path('api/units/create/', views.create_unit, name='create_unit'),
    path('api/units/update/<int:id>/', views.update_unit, name='update_unit'),
    path('api/units/delete/<int:id>/', views.delete_unit, name='delete_unit'),
    
    # Notifications URLs
    path('api/notifications/', views.list_notifications, name='list_notifications'),
    path('api/maintenance-requests/read/<int:request_id>/', views.mark_request_as_read, name='mark_request_as_read'),
    
    # Manage a specific maintenance request
    path('api/maintenance-requests/manage/<int:request_id>/', views.manage_maintenance_request, name='manage_maintenance_request'),

]


