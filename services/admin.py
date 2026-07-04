from django.contrib import admin
from .models import ServiceCategory, Service, Booking


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'vendor', 'price', 'duration', 'status', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('rating', 'total_reviews', 'created_at', 'updated_at')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('service', 'customer', 'booking_date', 'booking_time', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'booking_date', 'created_at')
    search_fields = ('service__name', 'customer__username', 'customer__email')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'booking_date'



