from django.db import models
from django.conf import settings


class Schedule(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    bus = models.ForeignKey('buses.Bus', on_delete=models.CASCADE, related_name='schedules')
    route = models.ForeignKey('routes.Route', on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    operating_days = models.JSONField(default=list, help_text='List of operating day numbers (0=Mon)')
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField()
    effective_until = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'

    def __str__(self):
        return f'{self.bus.bus_number} | {self.route} | {self.departure_time}'


class ScheduleStop(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='schedule_stops')
    route_stop = models.ForeignKey('routes.RouteStop', on_delete=models.CASCADE)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    fare_from_origin = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Schedule Stop'
        verbose_name_plural = 'Schedule Stops'
        ordering = ['route_stop__sequence']

    def __str__(self):
        return f'{self.schedule} - {self.route_stop.name}'
