from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from products.models import Product
from services.models import Service, Booking
from orders.models import Order, OrderItem
from payments.models import Payment
from accounts.models import User, VendorProfile


@login_required
def vendor_dashboard(request):
    """Vendor dashboard."""
    if not request.user.is_vendor():
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('products:home')
    
    # Statistics
    total_products = Product.objects.filter(vendor=request.user).count()
    active_products = Product.objects.filter(vendor=request.user, is_active=True).count()
    total_services = Service.objects.filter(vendor=request.user).count()
    active_services = Service.objects.filter(vendor=request.user, status='available').count()
    
    # Orders
    vendor_orders = Order.objects.filter(items__product__vendor=request.user).distinct()
    total_orders = vendor_orders.count()
    pending_orders = vendor_orders.filter(status='pending').count()
    completed_orders = vendor_orders.filter(status='delivered').count()
    
    # Revenue
    total_revenue = OrderItem.objects.filter(
        product__vendor=request.user,
        order__status__in=['confirmed', 'processing', 'shipped', 'delivered']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Recent orders
    recent_orders = vendor_orders[:10]
    
    # Bookings
    bookings = Booking.objects.filter(service__vendor=request.user)
    total_bookings = bookings.count()
    pending_bookings = bookings.filter(status='pending').count()
    recent_bookings = bookings[:10]
    
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'total_services': total_services,
        'active_services': active_services,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'dashboard/vendor_dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Admin dashboard."""
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admin access required.')
        return redirect('products:home')
    
    # User statistics
    total_users = User.objects.count()
    customers = User.objects.filter(role='customer').count()
    vendors = User.objects.filter(role='vendor').count()
    admins = User.objects.filter(role='admin').count()
    
    # Product statistics
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    low_stock_products = Product.objects.filter(stock__lt=10, is_active=True).count()
    
    # Service statistics
    total_services = Service.objects.count()
    active_services = Service.objects.filter(status='available').count()
    
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='delivered').count()
    total_sales = Order.objects.filter(status__in=['confirmed', 'processing', 'shipped', 'delivered']).aggregate(
        total=Sum('total')
    )['total'] or 0
    
    # Payment statistics
    total_payments = Payment.objects.count()
    completed_payments = Payment.objects.filter(status='completed').count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent activity
    recent_orders = Order.objects.all()[:10]
    recent_users = User.objects.all()[:10]
    
    # Monthly sales (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_sales = Order.objects.filter(
        created_at__gte=six_months_ago,
        status__in=['confirmed', 'processing', 'shipped', 'delivered']
    ).extra(
        select={'month': "DATE_FORMAT(created_at, '%%Y-%%m')"}
    ).values('month').annotate(
        total=Sum('total'),
        count=Count('id')
    ).order_by('month')
    
    context = {
        'total_users': total_users,
        'customers': customers,
        'vendors': vendors,
        'admins': admins,
        'total_products': total_products,
        'active_products': active_products,
        'low_stock_products': low_stock_products,
        'total_services': total_services,
        'active_services': active_services,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_sales': total_sales,
        'total_payments': total_payments,
        'completed_payments': completed_payments,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'recent_users': recent_users,
        'monthly_sales': monthly_sales,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def vendor_products(request):
    """Vendor's product management."""
    if not request.user.is_vendor():
        messages.error(request, 'Access denied.')
        return redirect('products:home')
    
    products = Product.objects.filter(vendor=request.user)
    
    context = {
        'products': products,
    }
    return render(request, 'dashboard/vendor_products.html', context)


@login_required
def vendor_services(request):
    """Vendor's service management."""
    if not request.user.is_vendor():
        messages.error(request, 'Access denied.')
        return redirect('products:home')
    
    services = Service.objects.filter(vendor=request.user)
    
    context = {
        'services': services,
    }
    return render(request, 'dashboard/vendor_services.html', context)

