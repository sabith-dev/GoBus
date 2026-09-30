from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    bus = models.ForeignKey('buses.Bus', on_delete=models.CASCADE, related_name='reviews')
    agency = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agency_reviews', null=True, blank=True)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    cleanliness_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    punctuality_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    comfort_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']

    def __str__(self):
        return f'Review by {self.user.username} - {self.rating}/5'


class ReviewReply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')
    replied_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Review Reply'
        verbose_name_plural = 'Review Replies'
        ordering = ['created_at']

    def __str__(self):
        return f'Reply to {self.review} by {self.replied_by.username}'
