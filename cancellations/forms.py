from django import forms
from .models import Cancellation


class CancellationForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Reason for Cancellation',
        help_text='Please provide a reason for cancelling this booking'
    )
