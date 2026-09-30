from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = [
        ('booking', 'Booking'),
        ('payment', 'Payment'),
        ('cancellation', 'Cancellation'),
        ('promotion', 'Promotion'),
        ('system', 'System'),
        ('tracking', 'Tracking'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.user.username}'

    @property
    def mark_as_read(self):
        self.is_read = True
        self.save()
