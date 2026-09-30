from django.db import models
from django.conf import settings


class Route(models.Model):
    agency = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='routes')
    name = models.CharField(max_length=200)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    estimated_duration = models.DurationField(help_text='Estimated travel duration')
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'

    def __str__(self):
        return f'{self.origin} → {self.destination}'


class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    sequence = models.PositiveIntegerField()
    arrival_offset = models.DurationField(help_text='Time from origin')
    departure_offset = models.DurationField(help_text='Time from origin')
    fare_from_origin = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Route Stop'
        verbose_name_plural = 'Route Stops'
        ordering = ['sequence']
        unique_together = ['route', 'sequence']

    def __str__(self):
        return f'{self.route} - Stop {self.sequence}: {self.name}'
