from django.db import models
from django.conf import settings
import uuid


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    schedule = models.ForeignKey('schedules.Schedule', on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField(auto_now_add=True)
    travel_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    passenger_name = models.CharField(max_length=200)
    passenger_email = models.EmailField()
    passenger_phone = models.CharField(max_length=17)
    pickup_point = models.CharField(max_length=200, blank=True)
    dropoff_point = models.CharField(max_length=200, blank=True)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']

    def __str__(self):
        return f'Booking {self.booking_id} - {self.passenger_name}'


class BookingSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='seats')
    seat = models.ForeignKey('buses.Seat', on_delete=models.CASCADE, related_name='bookings')
    passenger_name = models.CharField(max_length=200)
    passenger_age = models.PositiveIntegerField(blank=True, null=True)
    passenger_gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Booking Seat'
        verbose_name_plural = 'Booking Seats'
        unique_together = ['seat', 'booking']

    def __str__(self):
        return f'{self.booking} - {self.seat.seat_number}'


class SeatLock(models.Model):
    seat = models.ForeignKey('buses.Seat', on_delete=models.CASCADE, related_name='locks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    schedule = models.ForeignKey('schedules.Schedule', on_delete=models.CASCADE)
    locked_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Seat Lock'
        verbose_name_plural = 'Seat Locks'

    def __str__(self):
        return f'Lock: {self.seat.seat_number} by {self.user.username}'
