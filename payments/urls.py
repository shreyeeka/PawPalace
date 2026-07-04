from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<str:order_number>/', views.process_payment, name='process_payment'),
    path('esewa/<str:order_number>/', views.esewa_payment, name='esewa_payment'),
    path('detail/<str:order_number>/', views.payment_detail, name='payment_detail'),

    # Stripe Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
]
