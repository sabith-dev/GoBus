from django.contrib import admin
from .models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'offer_type', 'discount_value', 'min_booking_amount', 'is_active', 'valid_from', 'valid_until']
    list_filter = ['is_active', 'offer_type', 'valid_until']
    list_editable = ['is_active']
    search_fields = ['title', 'code', 'description']
    ordering = ['-created_at']