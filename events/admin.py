from django.contrib import admin
from .models import Event, Booking, Category, Payment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'city', 'date', 'available_seats', 'price', 'is_active']
    list_filter = ['category', 'city', 'is_active']
    search_fields = ['title', 'venue', 'city']
    list_editable = ['is_active']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['confirmation_code', 'user', 'event', 'quantity', 'total_price', 'status', 'booked_at']
    list_filter = ['status']
    search_fields = ['confirmation_code', 'user__username', 'event__title']
    readonly_fields = ['confirmation_code', 'booked_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'booking', 'card_holder', 'card_last4', 'amount', 'status', 'paid_at']
    list_filter = ['status']
    readonly_fields = ['transaction_id', 'paid_at']
