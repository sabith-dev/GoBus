from django import forms
from .models import Route, RouteStop


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'origin', 'destination', 'distance_km', 'estimated_duration', 'base_fare', 'is_active']
        widgets = {
            'estimated_duration': forms.TimeInput(attrs={'type': 'time'}),
        }


class RouteStopForm(forms.ModelForm):
    class Meta:
        model = RouteStop
        fields = ['name', 'address', 'city', 'sequence', 'arrival_offset', 'departure_offset', 'fare_from_origin', 'is_active']
        widgets = {
            'arrival_offset': forms.TimeInput(attrs={'type': 'time'}),
            'departure_offset': forms.TimeInput(attrs={'type': 'time'}),
        }
