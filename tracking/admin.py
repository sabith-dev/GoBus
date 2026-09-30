from django.contrib import admin
from .models import BusLocation, TrackingSession


@admin.register(BusLocation)
class BusLocationAdmin(admin.ModelAdmin):
    list_display = ['bus', 'latitude', 'longitude', 'speed', 'current_stop', 'timestamp']
    list_filter = ['is_on_time']


@admin.register(TrackingSession)
class TrackingSessionAdmin(admin.ModelAdmin):
    list_display = ['bus', 'schedule', 'is_active', 'started_at']
    list_filter = ['is_active']
