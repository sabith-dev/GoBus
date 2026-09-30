from django.db import models
from django.conf import settings


class BusType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    total_seats = models.PositiveIntegerField()
    is_sleeper = models.BooleanField(default=False)
    is_ac = models.BooleanField(default=True)
    amenities = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Bus Type'
        verbose_name_plural = 'Bus Types'

    def __str__(self):
        return self.name


class Bus(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]

    agency = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buses')
    bus_type = models.ForeignKey(BusType, on_delete=models.CASCADE, related_name='buses')
    bus_number = models.CharField(max_length=20, unique=True)
    bus_name = models.CharField(max_length=100)
    total_seats = models.PositiveIntegerField()
    seat_layout = models.JSONField(default=dict, help_text='JSON seat layout configuration')
    image = models.ImageField(upload_to='bus_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_live_trackable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bus'
        verbose_name_plural = 'Buses'

    def __str__(self):
        return f'{self.bus_name} ({self.bus_number})'


class Seat(models.Model):
    SEAT_TYPE_CHOICES = [
        ('seater', 'Seater'),
        ('sleeper', 'Sleeper'),
        ('window', 'Window'),
        ('aisle', 'Aisle'),
    ]

    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=5)
    seat_type = models.CharField(max_length=20, choices=SEAT_TYPE_CHOICES, default='seater')
    deck = models.PositiveIntegerField(default=1, help_text='1 for lower deck, 2 for upper deck')
    row = models.PositiveIntegerField()
    column = models.PositiveIntegerField()
    is_window = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    price_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)

    class Meta:
        verbose_name = 'Seat'
        verbose_name_plural = 'Seats'
        unique_together = ['bus', 'seat_number']

    def __str__(self):
        return f'{self.bus.bus_number} - Seat {self.seat_number}'
