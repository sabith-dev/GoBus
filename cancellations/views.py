from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Cancellation, CancellationPolicy
from bookings.models import Booking
from .forms import CancellationForm


@login_required
def cancellation_create_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, passenger=request.user)
    if request.method == 'POST':
        form = CancellationForm(request.POST)
        if form.is_valid():
            policies = CancellationPolicy.objects.filter(is_active=True)
            hours_before = (booking.travel_date - timezone.now().date()).days * 24
            fee_percentage = 0
            for policy in policies:
                if hours_before >= policy.hours_before_departure:
                    fee_percentage = policy.cancellation_fee_percentage
                    break

            cancellation_fee = booking.final_amount * (fee_percentage / 100)
            refund_amount = booking.final_amount - cancellation_fee

            cancellation = Cancellation.objects.create(
                booking=booking,
                cancelled_by=request.user,
                reason=form.cleaned_data['reason'],
                cancellation_fee=cancellation_fee,
                refund_amount=refund_amount,
            )
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, f'Booking cancelled. Refund of ₹{refund_amount} will be processed.')
            return redirect('bookings:booking_list')
    else:
        form = CancellationForm()
    return render(request, 'cancellations/create.html', {'form': form, 'booking': booking})


@login_required
def cancellation_list_view(request):
    cancellations = Cancellation.objects.filter(cancelled_by=request.user)
    return render(request, 'cancellations/list.html', {'cancellations': cancellations})


@login_required
def cancellation_detail_view(request, cancellation_id):
    cancellation = get_object_or_404(Cancellation, cancellation_id=cancellation_id)
    return render(request, 'cancellations/detail.html', {'cancellation': cancellation})
