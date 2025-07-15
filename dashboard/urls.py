from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('client-portal/', views.client_portal, name='client_portal'),
] 