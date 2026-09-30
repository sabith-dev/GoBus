from django import forms
from .models import Schedule, ScheduleStop


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['bus', 'route', 'departure_time', 'arrival_time', 'fare', 'operating_days', 'is_active', 'effective_from', 'effective_until']
        widgets = {
            'departure_time': forms.TimeInput(attrs={'type': 'time'}),
            'arrival_time': forms.TimeInput(attrs={'type': 'time'}),
            'effective_from': forms.DateInput(attrs={'type': 'date'}),
            'effective_until': forms.DateInput(attrs={'type': 'date'}),
            'operating_days': forms.CheckboxSelectMultiple,
        }


class ScheduleStopForm(forms.ModelForm):
    class Meta:
        model = ScheduleStop
        fields = ['route_stop', 'arrival_time', 'departure_time', 'fare_from_origin']
        widgets = {
            'arrival_time': forms.TimeInput(attrs={'type': 'time'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time'}),
        }
