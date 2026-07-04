from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='list'),
    path('vendor/', views.vendor_services, name='vendor_services'),
    path('add/', views.add_service, name='add_service'),
    path('edit/<slug:slug>/', views.edit_service, name='edit_service'),
    path('delete/<slug:slug>/', views.delete_service, name='delete_service'),
    path('book/<slug:slug>/', views.book_service, name='book'),
    path('booking/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('update-booking/<int:pk>/', views.update_booking_status, name='update_booking_status'),
    path('<slug:slug>/', views.service_detail, name='detail'),
]

