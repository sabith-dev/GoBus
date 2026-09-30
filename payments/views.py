from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Payment, Refund
from .forms import PaymentForm


@login_required
def payment_process_view(request, booking_id):
    from bookings.models import Booking
    booking = get_object_or_404(Booking, booking_id=booking_id, passenger=request.user)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = Payment.objects.create(
                booking=booking,
                user=request.user,
                amount=booking.final_amount,
                method=form.cleaned_data['method'],
                status='completed',
                paid_at=timezone.now(),
                transaction_id='TXN' + str(timezone.now().timestamp()).replace('.', '')
            )
            booking.status = 'confirmed'
            booking.save()
            messages.success(request, 'Payment successful!')
            return redirect('bookings:booking_detail', booking_id=booking.booking_id)
    else:
        form = PaymentForm()
    return render(request, 'payments/process.html', {'form': form, 'booking': booking})


@login_required
def payment_history_view(request):
    payments = Payment.objects.filter(user=request.user)
    return render(request, 'payments/history.html', {'payments': payments})


@login_required
def payment_detail_view(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    return render(request, 'payments/detail.html', {'payment': payment})
