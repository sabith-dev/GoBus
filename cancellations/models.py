from django.db import models
from django.conf import settings
import uuid


class CancellationPolicy(models.Model):
    name = models.CharField(max_length=100)
    hours_before_departure = models.PositiveIntegerField(help_text='Hours before departure')
    cancellation_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text='Percentage of ticket price')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cancellation Policy'
        verbose_name_plural = 'Cancellation Policies'
        ordering = ['hours_before_departure']

    def __str__(self):
        return f'{self.name} - {self.hours_before_departure}h before'


class Cancellation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('refunded', 'Refunded'),
    ]

    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='cancellations')
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cancellations')
    cancellation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cancellation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cancelled_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    admin_remarks = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Cancellation'
        verbose_name_plural = 'Cancellations'
        ordering = ['-cancelled_at']

    def __str__(self):
        return f'Cancellation {self.cancellation_id}'
