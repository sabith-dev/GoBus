from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.forms import AgencyProfileForm
from accounts.models import AgencyProfile, User
from bookings.models import Booking
from buses.forms import BusForm
from buses.layout import apply_layout
from buses.models import Bus, BusType, Seat
from cancellations.models import Cancellation
from notifications.models import Notification
from payments.models import Payment
from reviews.models import Review
from routes.forms import RouteForm
from routes.models import Route
from schedules.models import Schedule

from .forms import ScheduleForm


def _agency_schedules(user):
    return Schedule.objects.filter(bus__agency=user, route__agency=user)


def _agency_bookings(user):
    return Booking.objects.filter(schedule__bus__agency=user)


def _safe_profile(user):
    try:
        return user.agency_profile
    except AgencyProfile.DoesNotExist:
        return AgencyProfile.objects.create(
            user=user, agency_name=user.username, agency_code=user.username.upper()[:10],
        )
    except Exception:
        return None


def _generate_seats(bus):
    apply_layout(bus)


def _ensure_bus_types():
    if not BusType.objects.exists():
        BusType.objects.create(name='AC Seater', total_seats=40, is_ac=True, amenities=['AC', 'USB Charging', 'Water Bottle'])
        BusType.objects.create(name='AC Sleeper', total_seats=30, is_sleeper=True, is_ac=True, amenities=['AC', 'Comfortable Beds', 'Blanket'])
        BusType.objects.create(name='Non-AC Seater', total_seats=40, is_ac=False, amenities=['Reclining Seats'])
        return True
    return False


@login_required
def dashboard_view(request):
    today = date.today()
    _now = timezone.localtime()
    today_start = _now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today_start - timedelta(days=7)
    bookings = _agency_bookings(request.user)
    today_bookings = bookings.filter(booking_date=today)
    payments = Payment.objects.filter(status='completed', booking__schedule__bus__agency=request.user)
    today_earnings = payments.filter(paid_at__gte=today_start).aggregate(s=Sum('amount'))['s'] or 0
    week_earnings = payments.filter(paid_at__gte=week_ago).aggregate(s=Sum('amount'))['s'] or 0
    context = {
        'buses_count': request.user.buses.count(),
        'routes_count': request.user.routes.count(),
        'schedules_count': _agency_schedules(request.user).count(),
        'today_bookings': today_bookings.count(),
        'today_earnings': today_earnings,
        'week_earnings': week_earnings,
        'pending_bookings': bookings.filter(status='pending').count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
        'passenger_count': User.objects.filter(bookings__schedule__bus__agency=request.user).distinct().count(),
        'recent_bookings': today_bookings.select_related('passenger', 'schedule', 'schedule__bus')[:6],
        'all_bookings_count': bookings.count(),
    }
    return render(request, 'agency/dashboard.html', context)


@login_required
def profile_view(request):
    profile = _safe_profile(request.user)
    bookings = _agency_bookings(request.user)
    context = {
        'profile': profile,
        'buses_count': request.user.buses.count(),
        'routes_count': request.user.routes.count(),
        'schedules_count': Schedule.objects.filter(bus__agency=request.user).count(),
        'total_bookings': bookings.count(),
        'earnings_total': bookings.filter(
            status__in=['confirmed', 'completed', 'cancelled']
        ).aggregate(total=Sum('final_amount'))['total'] or 0,
    }
    return render(request, 'agency/profile.html', context)


@login_required
def settings_view(request):
    profile, _ = AgencyProfile.objects.get_or_create(
        user=request.user,
        defaults={'agency_name': request.user.username, 'agency_code': request.user.username.upper()[:10]},
    )
    if request.method == 'POST':
        form = AgencyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Agency settings updated successfully.')
            return redirect('agencies:settings')
    else:
        form = AgencyProfileForm(instance=profile)
    return render(request, 'agency/settings.html', {'form': form})


@login_required
def notifications_view(request):
    if request.method == 'POST':
        request.user.notifications.all().update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('agencies:notifications')
    notifications = request.user.notifications.all()
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
    }
    return render(request, 'agency/notifications.html', context)


@login_required
def bus_list_view(request):
    buses = request.user.buses.select_related('bus_type').all()
    queryset = request.GET.get('q', '').strip()
    if queryset:
        buses = buses.filter(Q(bus_number__icontains=queryset) | Q(bus_name__icontains=queryset))
    return render(request, 'agency/buses/list.html', {'buses': buses, 'query': queryset})


@login_required
def bus_add_view(request):
    _ensure_bus_types()
    if request.method == 'POST':
        form = BusForm(request.POST, request.FILES)
        if form.is_valid():
            bus = form.save(commit=False)
            bus.agency = request.user
            bus.save()
            _generate_seats(bus)
            Notification.objects.create(
                user=request.user,
                notification_type='system',
                title='Bus added',
                message=f'Bus {bus.bus_name} ({bus.bus_number}) has been added to your fleet.',
                link='/agency/buses/',
            )
            messages.success(request, 'Bus added successfully with seats generated.')
            return redirect('agencies:bus_list')
    else:
        form = BusForm()
    form.fields['bus_type'].queryset = BusType.objects.all()
    return render(request, 'agency/buses/add.html', {'form': form})


@login_required
def bus_edit_view(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id, agency=request.user)
    if request.method == 'POST':
        form = BusForm(request.POST, request.FILES, instance=bus)
        if form.is_valid():
            form.save()
            _generate_seats(bus)
            messages.success(request, 'Bus updated successfully.')
            return redirect('agencies:bus_details', bus_id=bus.id)
    else:
        form = BusForm(instance=bus)
    form.fields['bus_type'].queryset = BusType.objects.all()
    return render(request, 'agency/buses/edit.html', {'form': form, 'bus': bus})


@login_required
def bus_details_view(request, bus_id):
    bus = get_object_or_404(Bus.objects.select_related('bus_type'), id=bus_id, agency=request.user)
    context = {
        'bus': bus,
        'total_variants': bus.seats.count(),
        'active_schedules': bus.schedules.filter(is_active=True).count(),
        'bookings_count': Booking.objects.filter(schedule__bus=bus).count(),
        'latest_location': bus.locations.first(),
    }
    return render(request, 'agency/buses/details.html', context)


@login_required
def bus_seats_view(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id, agency=request.user)
    if request.method == 'POST' and request.POST.get('seat_id'):
        seat = get_object_or_404(Seat, id=request.POST['seat_id'], bus=bus)
        seat.is_available = not seat.is_available
        seat.save()
        messages.success(request, f'Seat {seat.seat_number} marked as {"available" if seat.is_available else "unavailable"}.')
        return redirect('agencies:bus_seats', bus_id=bus.id)
    seats = bus.seats.order_by('deck', 'row', 'column')
    return render(request, 'agency/buses/seats.html', {'bus': bus, 'seats': seats})


@login_required
def route_list_view(request):
    routes = request.user.routes.all().order_by('-created_at')
    return render(request, 'agency/routes/list.html', {'routes': routes})


@login_required
def route_add_view(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.agency = request.user
            route.save()
            messages.success(request, 'Route added successfully.')
            return redirect('agencies:route_list')
    else:
        form = RouteForm()
    return render(request, 'agency/routes/add.html', {'form': form})


@login_required
def route_edit_view(request, route_id):
    route = get_object_or_404(Route, id=route_id, agency=request.user)
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route updated successfully.')
            return redirect('agencies:route_list')
    else:
        form = RouteForm(instance=route)
    return render(request, 'agency/routes/edit.html', {'form': form, 'route': route})


@login_required
def schedule_list_view(request):
    schedules = (
        _agency_schedules(request.user)
        .select_related('bus', 'route')
        .order_by('departure_time')
    )
    return render(request, 'agency/schedules/list.html', {'schedules': schedules})


@login_required
def schedule_add_view(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST, agency=request.user)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.operating_days = [int(d) for d in form.cleaned_data.get('operating_days', [])]
            schedule.save()
            messages.success(request, 'Schedule added successfully.')
            return redirect('agencies:schedule_list')
    else:
        form = ScheduleForm(agency=request.user)
    return render(request, 'agency/schedules/add.html', {'form': form})


@login_required
def schedule_edit_view(request, schedule_id):
    schedule = get_object_or_404(
        _agency_schedules(request.user), id=schedule_id
    )
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule, agency=request.user)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.operating_days = [int(d) for d in form.cleaned_data.get('operating_days', [])]
            schedule.save()
            messages.success(request, 'Schedule updated successfully.')
            return redirect('agencies:schedule_list')
    else:
        form = ScheduleForm(instance=schedule, agency=request.user)
    return render(request, 'agency/schedules/edit.html', {'form': form, 'schedule': schedule})


@login_required
def passenger_list_view(request):
    passengers = (
        User.objects.filter(bookings__schedule__bus__agency=request.user)
        .distinct()
        .order_by('-date_joined')
    )
    return render(request, 'agency/passengers/list.html', {'passengers': passengers})


@login_required
def passenger_details_view(request, passenger_id):
    passenger = get_object_or_404(
        User.objects.filter(
            id=passenger_id,
            bookings__schedule__bus__agency=request.user,
        ).distinct(),
        id=passenger_id,
    )
    bookings = Booking.objects.filter(
        passenger=passenger, schedule__bus__agency=request.user
    ).select_related('schedule', 'schedule__bus', 'schedule__route')
    profile = getattr(passenger, 'passenger_profile', None)
    context = {
        'passenger': passenger,
        'profile': profile,
        'bookings': bookings,
        'total_spent': bookings.filter(status__in=['confirmed', 'completed']).aggregate(s=Sum('final_amount'))['s'] or 0,
    }
    return render(request, 'agency/passengers/details.html', context)


@login_required
def booking_list_view(request):
    bookings = (
        _agency_bookings(request.user)
        .select_related('passenger', 'schedule', 'schedule__bus', 'schedule__route')
    )
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'agency/bookings/list.html', {'bookings': bookings, 'status_filter': status_filter})


@login_required
def booking_details_view(request, booking_id):
    booking = get_object_or_404(
        _agency_bookings(request.user)
        .select_related('passenger', 'schedule', 'schedule__bus', 'schedule__bus__bus_type', 'schedule__route'),
        id=booking_id,
    )
    context = {
        'booking': booking,
        'seats': booking.seats.select_related('seat').all(),
        'cancellations': booking.cancellations.all(),
        'payment': Payment.objects.filter(booking=booking).first(),
    }
    return render(request, 'agency/bookings/details.html', context)


@login_required
def cancellation_list_view(request):
    cancellations = (
        Cancellation.objects.filter(booking__schedule__bus__agency=request.user)
        .select_related('booking', 'booking__passenger', 'booking__schedule')
    )
    return render(request, 'agency/cancellations/list.html', {'cancellations': cancellations})


@login_required
def earnings_view(request):
    today = date.today()
    payments = (
        Payment.objects.filter(status='completed', booking__schedule__bus__agency=request.user)
        .select_related('booking', 'booking__passenger', 'booking__schedule')
    )
    today_payments = [p for p in payments if p.paid_at and p.paid_at.date() == today]
    week_payments = [p for p in payments if p.paid_at and p.paid_at.date() >= today - timedelta(days=6)]
    month_payments = [p for p in payments if p.paid_at and p.paid_at.date() >= today.replace(day=1)]
    context = {
        'today_earnings': sum(p.amount for p in today_payments),
        'week_earnings': sum(p.amount for p in week_payments),
        'month_earnings': sum(p.amount for p in month_payments),
        'total_earnings': sum(p.amount for p in payments),
        'payments_count': len(payments),
        'recent_payments': payments[:10],
    }
    return render(request, 'agency/earnings/dashboard.html', context)


@login_required
def review_list_view(request):
    reviews = (
        Review.objects.filter(bus__agency=request.user)
        .select_related('user', 'bus')
        .distinct()
    )
    return render(request, 'agency/reviews/list.html', {'reviews': reviews})