import json
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.forms import PassengerProfileForm, UserUpdateForm
from accounts.models import PassengerProfile
from bookings.models import Booking, BookingSeat, SeatLock
from buses.models import Bus
from cancellations.models import Cancellation
from notifications.models import Notification
from payments.models import Payment
from referrals.models import Referral, ReferralCode
from reviews.forms import ReviewForm
from reviews.models import Review
from schedules.models import Schedule
from tracking.models import BusLocation
from wallets.models import Wallet


def _booked_seat_ids(schedule_id, travel_date):
    booking_ids = Booking.objects.filter(
        schedule_id=schedule_id, travel_date=travel_date,
        status__in=['pending', 'confirmed', 'completed'],
    ).values_list('id', flat=True)
    booked = BookingSeat.objects.filter(booking_id__in=booking_ids).values_list('seat_id', flat=True)
    locked = SeatLock.objects.filter(
        schedule_id=schedule_id, is_active=True, expires_at__gt=timezone.now(),
    ).values_list('seat_id', flat=True)
    return set(booked) | set(locked)


def _duration(schedule):
    delta = datetime.combine(date.today(), schedule.arrival_time) - datetime.combine(date.today(), schedule.departure_time)
    if delta.days < 0:
        delta += timedelta(days=1)
    hours, seconds = divmod(delta.total_seconds(), 3600)
    minutes = int(seconds // 60)
    return f'{int(hours)}h {minutes}m'


@login_required
def dashboard_view(request):
    today = date.today()
    bookings = request.user.bookings.all()
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    context = {
        'upcoming_count': bookings.filter(status__in=['pending', 'confirmed'], travel_date__gte=today).count(),
        'completed_count': bookings.filter(status='completed').count(),
        'total_bookings': bookings.count(),
        'wallet_balance': wallet.balance,
        'unread_count': request.user.notifications.filter(is_read=False).count(),
        'recent_bookings': bookings.select_related('schedule', 'schedule__bus', 'schedule__route')[:6],
    }
    return render(request, 'passenger/dashboard.html', context)


@login_required
def profile_view(request):
    profile = getattr(request.user, 'passenger_profile', None)
    return render(request, 'passenger/profile.html', {'profile': profile})


@login_required
def edit_profile_view(request):
    profile, _ = PassengerProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = PassengerProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('passengers:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = PassengerProfileForm(instance=profile)
    return render(request, 'passenger/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
def search_view(request):
    return render(request, 'passenger/search.html', {
        'source': request.GET.get('source', ''),
        'destination': request.GET.get('destination', ''),
        'date': request.GET.get('date', date.today().strftime('%Y-%m-%d')),
        'passengers': request.GET.get('passengers', '1'),
    })


@login_required
def bus_results_view(request):
    source = request.GET.get('source', '').strip()
    destination = request.GET.get('destination', '').strip()
    date_str = request.GET.get('date', '').strip()
    passengers = request.GET.get('passengers', '1').strip() or '1'
    schedules = []

    if source and destination:
        try:
            travel_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
        except ValueError:
            travel_date = date.today()
        weekday = travel_date.weekday()
        qs = Schedule.objects.filter(
            is_active=True,
            route__origin__icontains=source,
            route__destination__icontains=destination,
            effective_from__lte=travel_date,
        )
        if travel_date == date.today():
            qs = qs.filter(departure_time__gte=timezone.localtime().now().time())
        qs = qs.select_related('bus', 'bus__bus_type', 'route')
        for s in qs:
            if s.effective_until and s.effective_until < travel_date:
                continue
            days = [int(d) for d in (s.operating_days or [])]
            if days and weekday not in days:
                continue
            booked_ids = _booked_seat_ids(s.id, travel_date)
            total = s.bus.seats.count()
            s.seats_left = max(total - len(booked_ids), 0)
            s.travel_date = travel_date
            s.duration = _duration(s)
            rating_data = _bus_rating(s.bus)
            s.rating = rating_data[0] if rating_data else None
            s.review_count = rating_data[1] if rating_data else 0
            schedules.append(s)
        schedules.sort(key=lambda s: s.departure_time)

    context = {
        'schedules': schedules,
        'source': source,
        'destination': destination,
        'travel_date': date_str or date.today().strftime('%Y-%m-%d'),
        'passengers': passengers,
    }
    return render(request, 'passenger/bus_results.html', context)


def _bus_rating(bus):
    reviews = Review.objects.filter(bus=bus, is_approved=True)
    count = reviews.count()
    if not count:
        return None
    return round(sum(r.rating for r in reviews) / count, 1), count


@login_required
def bus_details_view(request, bus_id):
    bus = get_object_or_404(Bus.objects.select_related('bus_type'), id=bus_id)
    reviews = Review.objects.filter(bus=bus, is_approved=True).select_related('user')[:5]
    rating_data = _bus_rating(bus)
    context = {
        'bus': bus,
        'reviews': reviews,
        'rating': rating_data[0] if rating_data else None,
        'review_count': rating_data[1] if rating_data else 0,
        'schedules': bus.schedules.filter(is_active=True).select_related('route')[:5],
    }
    return render(request, 'passenger/bus_details.html', context)


@login_required
def seat_selection_view(request, schedule_id):
    schedule = get_object_or_404(
        Schedule.objects.select_related('bus', 'bus__bus_type', 'route'),
        id=schedule_id,
    )

    try:
        travel_date = datetime.strptime(request.POST.get('date') or request.GET.get('date', ''), '%Y-%m-%d').date()
    except ValueError:
        travel_date = date.today()

    if request.method == 'POST':
        raw_ids = request.POST.get('seat_ids', '')
        seat_id_list = [int(x) for x in raw_ids.split(',') if x.strip().isdigit()]
        if not seat_id_list:
            messages.error(request, 'Please select at least one seat.')
            return redirect('passengers:seat_selection', schedule_id=schedule.id)
        booked_ids = _booked_seat_ids(schedule.id, travel_date)
        seats = schedule.bus.seats.filter(id__in=seat_id_list, is_available=True).exclude(id__in=booked_ids)
        if not seats.exists():
            messages.error(request, 'The selected seats are no longer available.')
            return redirect('passengers:seat_selection', schedule_id=schedule.id)

        total = Decimal('0.00')
        booking = Booking(
            passenger=request.user,
            schedule=schedule,
            travel_date=travel_date,
            status='pending',
            passenger_name=request.user.get_full_name() or request.user.username,
            passenger_email=request.user.email or '',
            passenger_phone=request.user.phone_number or '',
        )
        booking.save()
        for seat in seats:
            price = schedule.fare * seat.price_multiplier
            BookingSeat.objects.create(
                booking=booking, seat=seat,
                passenger_name=booking.passenger_name,
                price=price,
            )
            total += price
        booking.total_amount = total
        booking.final_amount = total
        booking.save()
        messages.success(request, 'Boarding details saved. Complete the payment to confirm your seats.')
        return redirect('passengers:payment', booking_id=booking.id)

    booked_ids = _booked_seat_ids(schedule.id, travel_date)
    seats = schedule.bus.seats.order_by('deck', 'row', 'column')
    seat_data = [
        {
            'id': s.id,
            'num': s.seat_number,
            'deck': s.deck,
            'row': s.row,
            'col': s.column,
            'booked': s.id in booked_ids or not s.is_available,
            'price': format(schedule.fare * s.price_multiplier, '.2f'),
            'window': s.is_window,
            'pos': 'window' if s.is_window else ('middle' if s.column == 3 else 'aisle'),
            'type': s.seat_type,
        }
        for s in seats
    ]
    from buses.layout import layout_style
    context = {
        'schedule': schedule,
        'bus': schedule.bus,
        'travel_date': travel_date,
        'fare': schedule.fare,
        'booked_ids': booked_ids,
        'seats_json': json.dumps(seat_data),
        'layout_style': layout_style(schedule.bus),
        'bus_type_name': schedule.bus.bus_type.name,
        'is_sleeper': schedule.bus.bus_type.is_sleeper,
    }
    return render(request, 'passenger/seat_selection.html', context)


@login_required
def passenger_details_view(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('schedule', 'schedule__bus', 'schedule__bus__bus_type', 'schedule__route'),
        id=booking_id,
        passenger=request.user,
    )
    context = {
        'booking': booking,
        'seats': booking.seats.select_related('seat').all(),
        'payment': Payment.objects.filter(booking=booking).first(),
        'cancellation': booking.cancellations.first(),
    }
    return render(request, 'passenger/passenger_details.html', context)


@login_required
def payment_view(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('schedule', 'schedule__bus', 'schedule__bus__bus_type', 'schedule__route'),
        id=booking_id,
        passenger=request.user,
        status='pending',
    )
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        method = request.POST.get('method', 'upi')
        if method == 'wallet':
            if wallet.balance < booking.final_amount:
                messages.error(request, 'Insufficient wallet balance. Please add money to your wallet or choose another method.')
                return redirect('passengers:payment', booking_id=booking.id)
            wallet.deduct_money(booking.final_amount, description=f'Bus booking {booking.booking_id}')

        Payment.objects.create(
            booking=booking,
            user=request.user,
            amount=booking.final_amount,
            method=method if method in ['upi', 'card', 'netbanking', 'wallet'] else 'upi',
            status='completed',
            transaction_id=f'TXN{booking.booking_id.hex[:10].upper()}',
            paid_at=timezone.now(),
        )
        booking.status = 'confirmed'
        booking.save()
        booking.seats.update(is_booked=True)
        Notification.objects.create(
            user=request.user,
            notification_type='booking',
            title='Booking confirmed!',
            message=f'Your booking {booking.booking_id} for {booking.schedule.route} on {booking.travel_date} has been confirmed.',
            link=f'/passenger/booking/{booking.id}/ticket/',
        )
        Notification.objects.create(
            user=booking.schedule.bus.agency,
            notification_type='booking',
            title='New booking received',
            message=f'{booking.passenger_name} booked a seat on {booking.schedule.bus.bus_name} for {booking.travel_date}.',
            link=f'/agency/bookings/{booking.id}/',
        )
        return redirect('passengers:booking_confirmation', booking_id=booking.id)

    context = {
        'booking': booking,
        'amount': booking.final_amount,
        'wallet_balance': wallet.balance,
    }
    return render(request, 'passenger/payment.html', context)


@login_required
def booking_confirmation_view(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('schedule', 'schedule__bus', 'schedule__route'),
        id=booking_id,
        passenger=request.user,
    )
    context = {
        'booking': booking,
        'payment': Payment.objects.filter(booking=booking).first(),
        'seats': booking.seats.select_related('seat').all(),
    }
    return render(request, 'passenger/booking_confirmation.html', context)


@login_required
def ticket_view(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('schedule', 'schedule__bus', 'schedule__bus__bus_type', 'schedule__route', 'review'),
        id=booking_id,
        passenger=request.user,
    )
    context = {
        'booking': booking,
        'seats': booking.seats.select_related('seat').all(),
        'payment': Payment.objects.filter(booking=booking).first(),
    }
    return render(request, 'passenger/ticket.html', context)


@login_required
def my_bookings_view(request):
    today = date.today()
    all_bookings = request.user.bookings.select_related('schedule', 'schedule__bus', 'schedule__route')
    upcoming = all_bookings.filter(status__in=['pending', 'confirmed'], travel_date__gte=today)
    completed = all_bookings.filter(status='completed').union(all_bookings.filter(status='confirmed', travel_date__lt=today))
    cancelled = all_bookings.filter(status='cancelled')
    context = {
        'upcoming': upcoming,
        'completed': completed,
        'cancelled': cancelled,
    }
    return render(request, 'passenger/my_bookings.html', context)


@login_required
def booking_details_view(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('schedule', 'schedule__bus', 'schedule__route'),
        id=booking_id,
        passenger=request.user,
    )
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, 'Please provide a reason for cancellation.')
            return redirect('passengers:booking_details', booking_id=booking.id)
        if booking.status not in ('pending', 'confirmed'):
            messages.error(request, 'This booking cannot be cancelled.')
            return redirect('passengers:booking_details', booking_id=booking.id)
        Cancellation.objects.create(
            booking=booking,
            cancelled_by=request.user,
            reason=reason,
            status='pending',
            refund_amount=booking.final_amount,
        )
        booking.status = 'cancelled'
        booking.save()
        booking.seats.update(is_booked=False)
        Notification.objects.create(
            user=request.user,
            notification_type='cancellation',
            title='Cancellation requested',
            message=f'Your cancellation request for booking {booking.booking_id} has been submitted.',
            link=f'/passenger/cancellations/',
        )
        Notification.objects.create(
            user=booking.schedule.bus.agency,
            notification_type='cancellation',
            title='Booking cancellation request',
            message=f'{booking.passenger_name} requested cancellation for booking {booking.booking_id}.',
            link=f'/agency/cancellations/',
        )
        messages.success(request, 'Cancellation requested successfully.')
        return redirect('passengers:booking_details', booking_id=booking.id)

    context = {
        'booking': booking,
        'seats': booking.seats.select_related('seat').all(),
        'payment': Payment.objects.filter(booking=booking).first(),
    }
    return render(request, 'passenger/booking_details.html', context)


@login_required
def cancellations_view(request):
    cancellations = (
        Cancellation.objects.filter(cancelled_by=request.user)
        .select_related('booking', 'booking__schedule', 'booking__schedule__bus', 'booking__schedule__route')
    )
    return render(request, 'passenger/cancellations.html', {'cancellations': cancellations})


@login_required
def wallet_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except (TypeError, ValueError, InvalidOperation):
            amount = Decimal('0')
        if amount <= 0:
            messages.error(request, 'Please enter a valid amount.')
        else:
            wallet.add_money(amount)
            messages.success(request, f'₹{amount} added to your wallet.')
        return redirect('passengers:wallet')
    context = {
        'wallet': wallet,
        'transactions': wallet.transactions.all(),
    }
    return render(request, 'passenger/wallet.html', context)


@login_required
def referrals_view(request):
    code, _ = ReferralCode.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        Referral.objects.create(
            referrer=request.user,
            referral_code=code,
            status='pending',
        )
        Notification.objects.create(
            user=request.user,
            notification_type='system',
            title='Referral shared',
            message=f'Invite sent with your code {code.code}. Earn ₹{code.bonus_amount} when they complete a ride.',
            link='/passenger/referrals/',
        )
        messages.success(request, 'Referral invite sent successfully.')
        return redirect('passengers:referrals')
    referrals = Referral.objects.filter(referrer=request.user)
    context = {
        'referral_code': code,
        'total_referrals': code.total_referrals,
        'pending_count': referrals.filter(status='pending').count(),
        'completed_count': referrals.filter(status='completed').count(),
        'bonus_amount': code.bonus_amount,
        'referrals': referrals,
    }
    return render(request, 'passenger/referrals.html', context)


@login_required
def notifications_view(request):
    if request.method == 'POST':
        request.user.notifications.all().update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('passengers:notifications')
    notifications = request.user.notifications.all()
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
    }
    return render(request, 'passenger/notifications.html', context)


@login_required
def reviews_view(request):
    reviews = request.user.reviews.select_related('bus').all()
    eligible = (
        request.user.bookings
        .filter(status__in=['confirmed', 'completed'], review__isnull=True)
        .select_related('schedule', 'schedule__bus')
        .exclude(travel_date__gt=date.today())
    ).first()

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        form = ReviewForm(request.POST)
        booking = Booking.objects.filter(
            id=booking_id, passenger=request.user,
            status__in=['confirmed', 'completed'],
        ).first()
        if form.is_valid() and booking:
            review = form.save(commit=False)
            review.booking = booking
            review.user = request.user
            review.bus = booking.schedule.bus
            review.is_approved = True
            review.save()
            if review.bus.agency:
                Notification.objects.create(
                    user=review.bus.agency,
                    notification_type='system',
                    title='New bus review',
                    message=f'A passenger rated {review.bus.bus_name} {review.rating}/5.',
                    link='/agency/reviews/',
                )
            messages.success(request, 'Thank you! Your review has been submitted.')
            return redirect('passengers:reviews')
        messages.error(request, 'Could not submit review. Please check your booking and try again.')
        return redirect('passengers:reviews')

    context = {
        'reviews': reviews,
        'eligible_booking': eligible,
        'form': ReviewForm(),
    }
    return render(request, 'passenger/reviews.html', context)


@login_required
def live_tracking_view(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('schedule', 'schedule__bus', 'schedule__route'),
        id=booking_id,
        passenger=request.user,
    )
    location = booking.schedule.bus.locations.first()
    context = {
        'booking': booking,
        'bus': booking.schedule.bus,
        'tracking_available': booking.schedule.bus.is_live_trackable and location is not None,
        'location': location,
        'current_stop': location.current_stop if location else 'Not started yet',
        'next_stop': location.next_stop if location else 'Yet to depart',
        'eta': (location.estimated_arrival.strftime('%I:%M %p') if location and location.estimated_arrival else '—'),
        'speed': location.speed if location else Decimal('0'),
        'is_on_time': location.is_on_time if location else True,
        'latitude': float(location.latitude) if location else 0.0,
        'longitude': float(location.longitude) if location else 0.0,
    }
    return render(request, 'passenger/live_tracking.html', context)