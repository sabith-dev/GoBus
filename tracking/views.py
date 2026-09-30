from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import BusLocation, TrackingSession


@login_required
def tracking_map_view(request, booking_id):
    return render(request, 'tracking/map.html', {'booking_id': booking_id})


@login_required
def get_bus_location_api(request, bus_id):
    location = BusLocation.objects.filter(bus_id=bus_id).first()
    if location:
        return JsonResponse({
            'latitude': str(location.latitude),
            'longitude': str(location.longitude),
            'speed': str(location.speed),
            'current_stop': location.current_stop,
            'next_stop': location.next_stop,
            'estimated_arrival': str(location.estimated_arrival) if location.estimated_arrival else None,
            'is_on_time': location.is_on_time,
            'timestamp': location.timestamp.isoformat(),
        })
    return JsonResponse({'error': 'Location not available'}, status=404)
