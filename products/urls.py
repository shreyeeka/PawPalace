from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('home/', views.home, name='home'),
    path('add/', views.add_product, name='add_product'),
    path('delete/<slug:slug>/', views.delete_product, name='delete_product'),
    path('vendor/', views.vendor_products, name='vendor_products'),
    path('category/<slug:slug>/', views.category_list, name='category'),
    path('edit/<slug:slug>/', views.edit_product, name='edit_product'),  # ✅ add this
    path('<slug:slug>/', views.product_detail, name='detail'),
]
