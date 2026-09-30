from django.contrib import admin
from .models import Booking, BookingSeat, SeatLock


class BookingSeatInline(admin.TabularInline):
    model = BookingSeat
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'passenger', 'schedule', 'travel_date', 'status', 'final_amount', 'created_at']
    list_filter = ['status', 'travel_date']
    search_fields = ['booking_id', 'passenger_name', 'passenger_email']
    inlines = [BookingSeatInline]


@admin.register(SeatLock)
class SeatLockAdmin(admin.ModelAdmin):
    list_display = ['seat', 'user', 'schedule', 'locked_at', 'expires_at', 'is_active']
    list_filter = ['is_active']
