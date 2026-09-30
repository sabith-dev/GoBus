from django import forms
from .models import Booking, BookingSeat


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['passenger_name', 'passenger_email', 'passenger_phone', 'pickup_point', 'dropoff_point', 'special_requests', 'travel_date']


class BookingSeatForm(forms.ModelForm):
    class Meta:
        model = BookingSeat
        fields = ['passenger_name', 'passenger_age', 'passenger_gender']


class SeatSelectionForm(forms.Form):
    seat_ids = forms.CharField(widget=forms.HiddenInput(), help_text='Comma-separated seat IDs')
