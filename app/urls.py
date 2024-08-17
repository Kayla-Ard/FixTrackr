from django.urls import path
from . import views

urlpatterns = [
    # Tenant URLs
    path('', views.tenant_home, name='tenant_home'),
    path('submit-request/', views.submit_request, name='submit_request'),
    path('check-request-status/', views.check_request_status, name='check_request_status'),
    path('progress-check/', views.progress_check, name='progress_check'),  # Add this line for progress check

    # Property Manager API URLs
    path('api/property-managers/', views.property_managers_api, name='property_managers_api'),
    path('api/property-manager-details/<int:id>/', views.property_manager_details_api, name='property_manager_details_api'),

    # Maintenance Request API URLs
    path('api/submit-request/', views.submit_request_api, name='submit_request_api'),
    path('api/check-status/', views.check_status_api, name='check_status_api'),
    path('api/requests/', views.api_get_requests, name='api_get_requests'),

    # Example protected view URL
    path('api/protected/', views.ExampleProtectedView.as_view(), name='example_protected_view'),
]