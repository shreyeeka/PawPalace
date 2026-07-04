from django.contrib import admin
from django.urls import path, include
from products import views as product_views
from payments import views as payment_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', product_views.home, name='home'),

    # Stripe Checkout (one-time payment)
    path('checkout/', payment_views.checkout, name='checkout'),
    path('create-checkout-session/', payment_views.create_checkout_session, name='create_checkout_session'),
    path('success/', payment_views.payment_success, name='payment_success'),
    path('cancel/', payment_views.payment_cancel, name='payment_cancel'),

    path('products/', include('products.urls', namespace='products')),
    path('services/', include('services.urls', namespace='services')),

    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('dashboard/', include('dashboard.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')





