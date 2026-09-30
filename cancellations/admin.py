from django.contrib import admin
from .models import Cancellation, CancellationPolicy


@admin.register(CancellationPolicy)
class CancellationPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'hours_before_departure', 'cancellation_fee_percentage', 'is_active']
    list_filter = ['is_active']


@admin.register(Cancellation)
class CancellationAdmin(admin.ModelAdmin):
    list_display = ['cancellation_id', 'booking', 'cancelled_by', 'status', 'cancellation_fee', 'refund_amount', 'cancelled_at']
    list_filter = ['status']
    search_fields = ['cancellation_id', 'booking__booking_id']
