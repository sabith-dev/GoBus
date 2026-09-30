from django.contrib import admin
from .models import Payment, Refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'booking', 'user', 'amount', 'method', 'status', 'paid_at']
    list_filter = ['status', 'method']
    search_fields = ['payment_id', 'transaction_id', 'user__username']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['refund_id', 'payment', 'amount', 'status', 'created_at']
    list_filter = ['status']
