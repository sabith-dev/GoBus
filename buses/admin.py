from django.contrib import admin
from .models import Bus, BusType, Seat


@admin.register(BusType)
class BusTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_seats', 'is_sleeper', 'is_ac']
    search_fields = ['name']


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ['bus_name', 'bus_number', 'agency', 'bus_type', 'total_seats', 'status']
    list_filter = ['status', 'bus_type']
    search_fields = ['bus_name', 'bus_number']


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['bus', 'seat_number', 'seat_type', 'deck', 'is_window']
    list_filter = ['seat_type', 'deck']
