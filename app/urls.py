from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('app/', views.propertymanagers, name='propertymanagers'),
    path('app/details/<int:id>', views.details, name='details'),
]