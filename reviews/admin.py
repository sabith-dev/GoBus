from django.contrib import admin
from .models import Review, ReviewReply


class ReviewReplyInline(admin.TabularInline):
    model = ReviewReply
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'bus', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved']
    search_fields = ['user__username', 'title', 'comment']
    inlines = [ReviewReplyInline]
