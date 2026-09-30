from django import forms
from .models import Bus, BusType, Seat


class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ['bus_type', 'bus_number', 'bus_name', 'total_seats', 'image', 'status', 'is_live_trackable']


class BusTypeForm(forms.ModelForm):
    class Meta:
        model = BusType
        fields = ['name', 'description', 'total_seats', 'is_sleeper', 'is_ac', 'amenities']


class SeatForm(forms.ModelForm):
    class Meta:
        model = Seat
        fields = ['seat_number', 'seat_type', 'deck', 'row', 'column', 'is_window', 'price_multiplier']
