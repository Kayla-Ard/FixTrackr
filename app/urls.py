from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    
    # Tenant URLs
    path('', views.tenant_home, name='tenant_home'),
    path('check-request-status/', views.check_request_status, name='check_request_status'),
    path('progress-check/', views.progress_check, name='progress_check_no_number'),
    path('progress-check/<str:request_number>/', views.progress_check, name='progress_check'), 
    path('submit-request/', views.submit_request, name='submit_request'),
    path('request_submitted/<str:request_number>/', views.request_submitted, name='request_submitted'),

    # Property Manager API URLs
    path('api/register-property-manager/', views.RegisterPropertyManager.as_view(), name='register_property_manager'),
    path('api/login/', views.Login.as_view(), name='login'),
    path('api/refresh-token/',TokenRefreshView.as_view(),name="refresh-token"),
    
    # Unit management URLs
    path('api/units/', views.GetUnits.as_view(), name='list_units'),
    path('api/units/create/', views.CreateUnit.as_view(), name='create_unit'),
    path('api/units/<int:pk>/', views.UnitsView.as_view(), name='unit-detail'),

    
    # Notifications URLs
    path('api/notifications/', views.GetNotifications.as_view(), name='list_notifications'),
    path('api/notifications/read/<int:pk>/', views.ReadNotification.as_view(), name='mark_request_as_read'),
    
    # Manage a specific maintenance request
    path('api/maintenance-requests/',views.GetMaintenanceRequests.as_view(), name = "get-requests"),
    path('api/submit-request/', views.CreateMaintenanceRequest.as_view(), name='create-request'),
    path('api/maintenance/<int:pk>/', views.GetMaintenanceRequest.as_view(), name='get_request'),
    path('api/maintenance/update/<int:pk>/', views.EditMaintenanceRequest.as_view(), name='update_request'),
]


