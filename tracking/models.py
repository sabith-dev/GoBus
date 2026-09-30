from django.db import models
from django.conf import settings


class BusLocation(models.Model):
    bus = models.ForeignKey('buses.Bus', on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text='Speed in km/h')
    heading = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Direction in degrees')
    current_stop = models.CharField(max_length=100, blank=True)
    next_stop = models.CharField(max_length=100, blank=True)
    estimated_arrival = models.TimeField(blank=True, null=True)
    is_on_time = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Bus Location'
        verbose_name_plural = 'Bus Locations'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.bus.bus_number} at ({self.latitude}, {self.longitude})'


class TrackingSession(models.Model):
    bus = models.ForeignKey('buses.Bus', on_delete=models.CASCADE, related_name='tracking_sessions')
    schedule = models.ForeignKey('schedules.Schedule', on_delete=models.CASCADE, related_name='tracking_sessions')
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)

    class Meta:
        verbose_name = 'Tracking Session'
        verbose_name_plural = 'Tracking Sessions'

    def __str__(self):
        return f'Tracking: {self.bus.bus_number}'
