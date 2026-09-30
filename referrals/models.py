from django.db import models
from django.conf import settings
import uuid


class ReferralCode(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_code')
    code = models.CharField(max_length=10, unique=True, default=uuid.uuid4().hex[:10].upper())
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=50)
    is_active = models.BooleanField(default=True)
    total_referrals = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Referral Code'
        verbose_name_plural = 'Referral Codes'

    def __str__(self):
        return f'{self.user.username} - {self.code}'


class Referral(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]

    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referred_by', null=True, blank=True)
    referral_code = models.ForeignKey(ReferralCode, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    bonus_credited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.referrer.username} referred {self.referred_user}'
