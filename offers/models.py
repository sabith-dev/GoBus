from django.db import models


class Offer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('flat', 'Flat Discount'),
        ('percent', 'Percentage Discount'),
    ]

    title = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True, help_text='Promo / coupon code')
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES, default='flat')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_booking_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True)
    tagline = models.CharField(max_length=120, blank=True, help_text='Short tagline shown on cards')
    icon = models.CharField(max_length=50, default='fa-tag', help_text='Font Awesome icon class')
    valid_from = models.DateField()
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.code})'

    def discount_label(self):
        if self.offer_type == 'percent':
            return f'{self.discount_value:.0f}% OFF'
        return f'₹{self.discount_value:,.0f} OFF'