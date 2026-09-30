from django.contrib import admin
from .models import Route, RouteStop


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1
    ordering = ['sequence']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'origin', 'destination', 'distance_km', 'base_fare', 'is_active']
    list_filter = ['is_active', 'agency']
    search_fields = ['name', 'origin', 'destination']
    inlines = [RouteStopInline]


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ['route', 'name', 'city', 'sequence', 'fare_from_origin']
    list_filter = ['route']
