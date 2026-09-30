from django import forms
from .models import Review, ReviewReply


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'cleanliness_rating', 'punctuality_rating', 'comfort_rating', 'is_anonymous']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'cleanliness_rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'punctuality_rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comfort_rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }


class ReviewReplyForm(forms.ModelForm):
    class Meta:
        model = ReviewReply
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
