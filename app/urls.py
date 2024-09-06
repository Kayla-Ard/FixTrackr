
from django.urls import path
from . import views


urlpatterns = [
    
    # Tenant URLs
    path('', views.tenant_home, name='tenant_home'),
    path('check-request-status/', views.check_request_status, name='check_request_status'),
    path('progress-check/', views.progress_check, name='progress_check_no_number'),
    path('progress-check/<str:request_number>/', views.progress_check, name='progress_check'), 
    path('submit-request/', views.submit_request, name='submit_request'),
    path('request_submitted/<str:request_number>/', views.request_submitted, name='request_submitted'),

    
    # Property Manager API URLs
    path('api/register-property-manager/', views.register_property_manager, name='register_property_manager'),
    path('api/login/', views.login, name='login'),
    
    # Unit management URLs
    path('api/units/', views.list_units, name='list_units'),
    path('api/units/create/', views.create_unit, name='create_unit'),
    path('api/units/update/<int:id>/', views.update_unit, name='update_unit'),
    path('api/units/delete/<int:id>/', views.delete_unit, name='delete_unit'),
    path('api/units/<int:id>/', views.get_unit_by_id, name='get_unit_by_id'),
    
    # Notifications URLs
    path('api/notifications/', views.list_notifications, name='list_notifications'),
    path('api/maintenance-requests/read/<int:request_id>/', views.mark_request_as_read, name='mark_request_as_read'),
    path('api/notifications/create/', views.create_notification, name='create_notification'),
    path('api/notifications/create-alert-notification/', views.create_alert_notification, name='create_alert_notification'),
    
    # Manage a specific maintenance request
    path('api/maintenance-requests/manage/<int:request_id>/', views.manage_maintenance_request, name='manage_maintenance_request'),
]


