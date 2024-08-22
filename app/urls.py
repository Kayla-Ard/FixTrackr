from django.urls import path
from . import views

urlpatterns = [
    
    # Tenant URLs
    path('', views.tenant_home, name='tenant_home'),
    path('submit-request/', views.submit_request, name='submit_request'),
    path('check-request-status/', views.check_request_status, name='check_request_status'),
    path('progress-check/', views.progress_check, name='progress_check_no_number'),
    path('progress-check/<str:request_number>/', views.progress_check, name='progress_check'), 

    # Property Manager API URLs
    path('api/register-property-manager/', views.register_property_manager, name='register_property_manager'),
    path('api/properties/', views.list_properties, name='list_properties'),
    path('api/properties/create/', views.create_property, name='create_property'),
    path('api/properties/update/<int:id>/', views.update_property, name='update_property'),
    path('api/properties/delete/<int:id>/', views.delete_property, name='delete_property'),
    path('api/maintenance-requests/', views.list_maintenance_requests, name='list_maintenance_requests'),
    path('api/maintenance-requests/update-status/<int:id>/', views.update_request_status, name='update_request_status'),

]

    # Example protected view URL
    # path('api/protected/', views.ExampleProtectedView.as_view(), name='example_protected_view'),
