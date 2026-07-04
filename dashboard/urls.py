from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/products/', views.vendor_products, name='vendor_products'),
    path('vendor/services/', views.vendor_services, name='vendor_services'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
]









