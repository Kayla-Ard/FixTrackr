from django.urls import path
from . import views

urlpatterns = [
    # HTML Views
    path('', views.main, name='main'),
    path('app/', views.propertymanagers, name='propertymanagers'),
    path('app/details/<int:id>', views.details, name='details'),
    path('submit-request/', views.submit_request, name='submit_request'),
    path('check-request-status/', views.check_request_status, name='check_request_status'),


    # RESTful API Endpoints
    path('api/requests/', views.api_get_requests, name='api_get_requests'),
    path('api/submit-request/', views.submit_request_api, name='submit_request_api'),
    path('api/check-status/', views.check_status_api, name='check_status_api'),
]