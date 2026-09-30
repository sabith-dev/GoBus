from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Booking, BookingSeat, SeatLock
from .forms import BookingForm


@login_required
def booking_create_view(request, schedule_id):
    if request.method == 'POST':
        seat_ids = request.POST.get('seat_ids', '').split(',')
        # Create booking logic
        messages.success(request, 'Booking created!')
        return redirect('bookings:booking_list')
    return render(request, 'bookings/create.html', {'schedule_id': schedule_id})


@login_required
def booking_list_view(request):
    bookings = Booking.objects.filter(passenger=request.user)
    return render(request, 'bookings/list.html', {'bookings': bookings})


@login_required
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    return render(request, 'bookings/detail.html', {'booking': booking})


@login_required
def booking_confirm_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, passenger=request.user)
    if request.method == 'POST':
        booking.status = 'confirmed'
        booking.save()
        messages.success(request, 'Booking confirmed!')
        return redirect('bookings:booking_detail', booking_id=booking.booking_id)
    return render(request, 'bookings/confirm.html', {'booking': booking})
