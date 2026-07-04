from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.text import slugify
from .models import Service, ServiceCategory, Booking
from .forms import BookingForm, ServiceForm

def service_list(request):
    services = Service.objects.filter(status='available')
    
    search_query = request.GET.get('search', '')
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    category_slug = request.GET.get('category', '')
    if category_slug:
        services = services.filter(category__slug=category_slug)
    
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = ServiceCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
    }
    return render(request, 'services/service_list.html', context)


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, status='available')
    related_services = Service.objects.filter(
        category=service.category,
        status='available'
    ).exclude(id=service.id)[:4]
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    return render(request, 'services/service_detail.html', context)


@login_required
def book_service(request, slug):
    service = get_object_or_404(Service, slug=slug, status='available')
    
    if not hasattr(request.user, 'is_customer') or not request.user.is_customer():
        messages.error(request, 'Only customers can book services.')
        return redirect('services:detail', slug=slug)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.service = service
            booking.customer = request.user
            booking.total_price = service.price
            booking.save()
            messages.success(request, 'Service booked successfully!')
            return redirect('services:booking_detail', pk=booking.pk)
    else:
        form = BookingForm()
    
    return render(request, 'services/book_service.html', {'service': service, 'form': form})


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    if not (request.user == booking.customer or
            request.user == booking.service.vendor or
            (hasattr(request.user, 'is_admin') and request.user.is_admin())):
        messages.error(request, 'You do not have permission to view this booking.')
        return redirect('services:list')
    
    return render(request, 'services/booking_detail.html', {'booking': booking})


@login_required
def my_bookings(request):
    if hasattr(request.user, 'is_customer') and request.user.is_customer():
        bookings = Booking.objects.filter(customer=request.user)
    elif hasattr(request.user, 'is_vendor') and request.user.is_vendor():
        bookings = Booking.objects.filter(service__vendor=request.user)
    else:
        bookings = Booking.objects.all()
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'services/my_bookings.html', {'page_obj': page_obj, 'status_filter': status_filter})


@login_required
def update_booking_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    if not (request.user == booking.service.vendor or
            (hasattr(request.user, 'is_admin') and request.user.is_admin())):
        messages.error(request, 'You do not have permission to update this booking.')
        return redirect('services:booking_detail', pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Booking.STATUS_CHOICES):
            booking.status = new_status
            booking.save()
            messages.success(request, 'Booking status updated successfully!')
        else:
            messages.error(request, 'Invalid status.')
    
    return redirect('services:booking_detail', pk=pk)


@login_required
def vendor_services(request):
    if not hasattr(request.user, 'is_vendor') or not request.user.is_vendor():
        messages.error(request, 'You do not have permission to view vendor services.')
        return redirect('services:list')
    
    services = Service.objects.filter(vendor=request.user)
    return render(request, 'services/vendor_services.html', {'services': services})


@login_required
def add_service(request):
    """Add a new service (vendor only)."""
    if not request.user.is_vendor():
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('services:list')
    
    form = ServiceForm()
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.vendor = request.user
            # Generate slug from name
            service.slug = slugify(service.name)
            # Ensure uniqueness
            base_slug = service.slug
            counter = 1
            while Service.objects.filter(slug=service.slug).exists():
                service.slug = f"{base_slug}-{counter}"
                counter += 1
            service.save()
            messages.success(request, "Service added successfully!")
            return redirect('dashboard:vendor_services')
    
    return render(request, 'services/add_service.html', {'form': form})


@login_required
def edit_service(request, slug):
    """Edit an existing service (vendor only, own services)."""
    if not request.user.is_vendor():
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('services:list')
    
    service = get_object_or_404(Service, slug=slug, vendor=request.user)
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('dashboard:vendor_services')
    else:
        form = ServiceForm(instance=service)
    
    return render(request, 'services/add_service.html', {'form': form, 'service': service, 'is_edit': True})


@login_required
def delete_service(request, slug):
    """Delete a service (vendor only, own services)."""
    if not request.user.is_vendor():
        messages.error(request, 'Access denied. Vendor access required.')
        return redirect('services:list')
    
    service = get_object_or_404(Service, slug=slug, vendor=request.user)
    
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully!')
        return redirect('dashboard:vendor_services')
    
    return render(request, 'services/delete_service.html', {'service': service})

