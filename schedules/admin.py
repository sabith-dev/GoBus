from django.contrib import admin
from .models import Schedule, ScheduleStop


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['bus', 'route', 'departure_time', 'arrival_time', 'fare', 'is_active']
    list_filter = ['is_active', 'bus', 'route']
    search_fields = ['bus__bus_number', 'route__name']


@admin.register(ScheduleStop)
class ScheduleStopAdmin(admin.ModelAdmin):
    list_display = ['schedule', 'route_stop', 'arrival_time', 'departure_time', 'fare_from_origin']
