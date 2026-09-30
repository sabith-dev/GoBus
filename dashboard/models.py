from django.db import models
from django.conf import settings


class Banner(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    link = models.URLField(blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    author = models.CharField(max_length=100, default='Admin')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=50, default='general')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.question[:80]


class PageContent(models.Model):
    SLUG_CHOICES = [
        ('privacy', 'Privacy Policy'),
        ('terms', 'Terms of Service'),
        ('about', 'About Us'),
        ('contact', 'Contact'),
    ]
    slug = models.CharField(max_length=50, unique=True, choices=SLUG_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    CATEGORY_CHOICES = [
        ('booking', 'Booking Issue'),
        ('payment', 'Payment Issue'),
        ('cancellation', 'Cancellation'),
        ('refund', 'Refund Request'),
        ('bus_quality', 'Bus Quality'),
        ('driver', 'Driver Issue'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=300)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True)
    admin_reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.subject[:50]}"


class EmergencyAlert(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='emergency_alerts')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='high')
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class LoginLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    username_attempted = models.CharField(max_length=150, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    browser = models.CharField(max_length=100, blank=True)
    device = models.CharField(max_length=100, blank=True)
    is_success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username_attempted} from {self.ip_address} - {'OK' if self.is_success else 'FAIL'}"


class FailedLogin(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    reason = models.CharField(max_length=200, default='Invalid credentials')
    attempt_count = models.IntegerField(default=1)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} - {self.ip_address} ({self.attempt_count} attempts)"


class IPRecord(models.Model):
    LIST_TYPE_CHOICES = [
        ('whitelist', 'Whitelist'),
        ('blacklist', 'Blacklist'),
    ]
    address = models.GenericIPAddressField()
    list_type = models.CharField(max_length=10, choices=LIST_TYPE_CHOICES)
    reason = models.CharField(max_length=300, blank=True)
    label = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['address', 'list_type']

    def __str__(self):
        return f"{self.address} ({self.list_type})"


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=200, blank=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"


class FestivalCampaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    coupon_code = models.CharField(max_length=30, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title


class FlashSale(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    coupon_code = models.CharField(max_length=30, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_uses = models.IntegerField(default=100)
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title


class MassNotification(models.Model):
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
        ('announcement', 'Announcement'),
    ]
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='email')
    target_role = models.CharField(max_length=30, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
