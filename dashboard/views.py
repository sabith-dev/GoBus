from collections import Counter
from datetime import timedelta
import csv
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .decorators import admin_required
from .models import (
    AuditLog, Banner, BlogPost, EmergencyAlert, FAQ,
    FailedLogin, FestivalCampaign, FlashSale, IPRecord, LoginLog,
    MassNotification, PageContent, SupportTicket,
)
from accounts.models import AgencyProfile, User
from bookings.models import Booking, BookingSeat
from buses.models import Bus, BusType
from notifications.models import Notification
from offers.models import Offer
from payments.models import Payment, Refund
from reviews.models import Review
from routes.models import Route
from schedules.models import Schedule
from wallets.models import Wallet, WalletTransaction

DEFAULT_COMMISSION_RATE = 10.0


def _is_admin(user):
    return bool(user.is_authenticated and (user.is_superuser or user.user_type == 'admin'))


def _attach_booking(obj):
    obj.user = obj.passenger
    obj.booked_at = obj.booking_date
    if obj.schedule_id:
        obj.bus = obj.schedule.bus
        obj.route = obj.schedule.route
    else:
        obj.bus = None
        obj.route = None
    obj.total_passengers = max(obj.seats.count(), 1)
    return obj


def _attach_agency(obj, session=None):
    obj.is_approved = obj.status == 'approved'
    obj.is_blacklisted = obj.status == 'suspended'
    rate = DEFAULT_COMMISSION_RATE
    if session:
        try:
            rate = float(session.get('commission_rate') or rate)
        except (TypeError, ValueError):
            rate = DEFAULT_COMMISSION_RATE
    obj.commission_rate = rate
    obj.total_revenue = float(
        Payment.objects.filter(
            status='completed', booking__schedule__bus__agency=obj.user_id
        ).aggregate(total=Sum('amount'))['total'] or 0
    )
    return obj


def _attach_bus(obj):
    first = obj.schedules.first()
    obj.route = first.route if first else None
    obj.is_featured = False
    obj.is_premium = False
    return obj


def _attach_offer(obj):
    obj.discount_type = 'percentage' if obj.offer_type == 'percent' else 'flat'
    obj.used_count = 0
    obj.max_uses = None
    return obj


def admin_login_view(request):
    if _is_admin(request.user):
        return redirect('admin_portal:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        ip = request.META.get('REMOTE_ADDR', '')
        ua = request.META.get('HTTP_USER_AGENT', '')

        if user is not None:
            if user.is_superuser or user.user_type == 'admin':
                login(request, user)
                LoginLog.objects.create(
                    user=user, username_attempted=username,
                    ip_address=ip, user_agent=ua, is_success=True
                )
                AuditLog.objects.create(
                    user=user, action='login', resource='admin_portal',
                    details='Admin login successful', ip_address=ip
                )
                messages.success(request, f'Welcome, {user.get_full_name() or user.username}!')
                return redirect('admin_portal:dashboard')
            else:
                LoginLog.objects.create(
                    username_attempted=username, ip_address=ip,
                    user_agent=ua, is_success=False, failure_reason='Not a superuser'
                )
                messages.error(request, 'Access denied. Only admin accounts can access the admin panel.')
        else:
            LoginLog.objects.create(
                username_attempted=username, ip_address=ip,
                user_agent=ua, is_success=False, failure_reason='Invalid credentials'
            )
            fl, created = FailedLogin.objects.get_or_create(
                username=username, ip_address=ip,
                defaults={'reason': 'Invalid credentials'}
            )
            if not created:
                fl.attempt_count += 1
                if fl.attempt_count >= 5:
                    fl.is_locked = True
                fl.save()
            messages.error(request, 'Invalid username or password.')

    return render(request, 'admin_portal/login.html')


def admin_logout_view(request):
    ip = request.META.get('REMOTE_ADDR', '')
    if request.user.is_authenticated:
        AuditLog.objects.create(
            user=request.user, action='logout', resource='admin_portal',
            details='Admin logout', ip_address=ip
        )
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('admin_portal:login')


@login_required
@admin_required
def admin_dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Agent stats
    total_agencies = AgencyProfile.objects.count()
    pending_agencies = AgencyProfile.objects.filter(status='pending').count()
    active_buses = Bus.objects.filter(status='active').count()
    total_routes = Route.objects.count()

    origin_counts = Counter(Route.objects.values_list('origin', flat=True))
    dest_counts = Counter(Route.objects.values_list('destination', flat=True))
    all_city_names = sorted(set(origin_counts) | set(dest_counts))
    total_cities = len(all_city_names)

    # Bookings
    bookings_q = Booking.objects.all()
    total_bookings = bookings_q.count()
    today_bookings = bookings_q.filter(booking_date=today).count()
    cancelled_bookings = bookings_q.filter(status='cancelled').count()
    total_passengers = User.objects.filter(user_type='passenger').count()
    total_users = User.objects.filter(user_type='passenger').count()

    # Revenue (confirmed / completed booking final amounts)
    completed_q = bookings_q.filter(status__in=['confirmed', 'completed'])
    total_revenue = float(completed_q.aggregate(total=Sum('final_amount'))['total'] or 0)
    today_revenue = float(completed_q.filter(booking_date=today).aggregate(total=Sum('final_amount'))['total'] or 0)
    weekly_revenue = float(completed_q.filter(booking_date__gte=week_ago).aggregate(total=Sum('final_amount'))['total'] or 0)
    monthly_revenue = float(completed_q.filter(booking_date__gte=month_ago).aggregate(total=Sum('final_amount'))['total'] or 0)

    # Recent bookings
    recent_bookings = [_attach_booking(b) for b in bookings_q.select_related('passenger', 'schedule__bus').order_by('-booking_date')[:10]]

    # Occupancy
    total_seats = Bus.objects.filter(status='active').aggregate(total=Sum('total_seats'))['total'] or 1
    booked_seats = bookings_q.filter(
        status__in=['confirmed', 'completed'],
        booking_date__gte=month_ago
    ).count()
    occupancy_rate = round((booked_seats / total_seats) * 100, 1)

    # Charts
    cities_chart_data = [
        {'name': c, 'departures': origin_counts.get(c, 0), 'arrivals': dest_counts.get(c, 0)}
        for c in all_city_names[:8]
    ]

    revenue_trend = []
    bookings_trend = []
    for i in range(30):
        day = today - timedelta(days=i)
        day_revenue = float(completed_q.filter(booking_date=day).aggregate(total=Sum('final_amount'))['total'] or 0)
        day_bookings = bookings_q.filter(booking_date=day).count()
        revenue_trend.append({'date': day.strftime('%d %b'), 'total': day_revenue})
        bookings_trend.append({'date': day.strftime('%d %b'), 'count': day_bookings})
    revenue_trend.reverse()
    bookings_trend.reverse()

    popular_cities = [
        {'name': c, 'departures': origin_counts.get(c, 0)}
        for c in all_city_names[:5]
    ]

    context = {
        'total_users': total_users,
        'total_agencies': total_agencies,
        'active_buses': active_buses,
        'total_bookings': total_bookings,
        'today_bookings': today_bookings,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'total_cities': total_cities,
        'total_routes': total_routes,
        'pending_agencies': pending_agencies,
        'cancelled_bookings': cancelled_bookings,
        'total_passengers': total_passengers,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'occupancy_rate': occupancy_rate,
        'recent_bookings': recent_bookings,
        'top_routes': Route.objects.annotate(
            booking_count=Count('schedules__bookings')
        ).order_by('-booking_count')[:5],
        'popular_cities': popular_cities,
        'revenue_chart_data': json.dumps(revenue_trend),
        'bookings_chart_data': json.dumps(bookings_trend),
        'cities_chart_data': json.dumps(cities_chart_data),
    }
    return render(request, 'admin_portal/dashboard.html', context)


@login_required
@admin_required
def manage_users(request):
    users = User.objects.filter(user_type='passenger')
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    if query:
        users = users.filter(
            Q(username__icontains=query) | Q(email__icontains=query) | Q(phone_number__icontains=query)
        )
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'verified':
        users = users.filter(email_verified=True)
    elif status_filter == 'unverified':
        users = users.filter(email_verified=False)

    if request.method == 'POST':
        action = request.POST.get('action') or request.POST.get('bulk_action')
        user_ids = request.POST.getlist('selected_users') or request.POST.getlist('user_ids')
        if action and user_ids:
            applied = 0
            for uid in user_ids:
                try:
                    user = User.objects.get(pk=uid)
                except User.DoesNotExist:
                    continue
                if action == 'delete':
                    user.delete()
                elif action == 'suspend':
                    user.is_active = False
                    user.save()
                elif action == 'activate':
                    user.is_active = True
                    user.save()
                elif action == 'verify':
                    user.email_verified = True
                    user.save()
                elif action == 'ban':
                    user.is_active = False
                    user.save()
                else:
                    continue
                applied += 1
                AuditLog.objects.create(
                    user=request.user, action=f'user_{action}',
                    resource=f'user:{uid}',
                    details=f'Action {action} on user {user.username}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            messages.success(request, f'Action "{action}" applied to {applied} user(s).')
            return redirect('admin_portal:users')

    return render(request, 'admin_portal/users.html', {
        'users': users, 'query': query, 'total': users.count(), 'status_filter': status_filter
    })


@login_required
@admin_required
def user_detail(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    bookings = [
        _attach_booking(b) for b in Booking.objects.filter(passenger=user_obj)
        .select_related('schedule__bus', 'schedule__route').order_by('-booking_date')[:20]
    ]
    payments = Payment.objects.filter(user=user_obj).select_related('booking').order_by('-created_at')[:20]
    wallet = Wallet.objects.filter(user=user_obj).first()
    wallet_txns = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')[:20] if wallet else []

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'verify':
            user_obj.email_verified = True
            user_obj.save()
            messages.success(request, f'{user_obj.username} verified.')
        elif action == 'suspend':
            user_obj.is_active = False
            user_obj.save()
            messages.success(request, f'{user_obj.username} suspended.')
        elif action == 'activate':
            user_obj.is_active = True
            user_obj.save()
            messages.success(request, f'{user_obj.username} activated.')
        elif action == 'delete':
            user_obj.delete()
            messages.success(request, f'{user_obj.username} deleted.')
            return redirect('admin_portal:users')
        AuditLog.objects.create(
            user=request.user, action=f'user_{action}',
            resource=f'user:{pk}',
            details=f'Action {action} on {user_obj.username}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return redirect('admin_portal:user_detail', pk=pk)

    return render(request, 'admin_portal/user_detail.html', {
        'profile_user': user_obj, 'bookings': bookings, 'payments': payments,
        'wallet': wallet, 'wallet_txns': wallet_txns
    })


@login_required
@admin_required
def manage_agencies(request):
    agencies = list(AgencyProfile.objects.select_related('user'))
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    if query:
        q = query.lower()
        agencies = [a for a in agencies if q in a.agency_name.lower() or q in (a.user.username or '').lower()]
    if status_filter == 'approved':
        agencies = [a for a in agencies if a.status == 'approved']
    elif status_filter == 'pending':
        agencies = [a for a in agencies if a.status == 'pending']
    elif status_filter == 'blacklisted':
        agencies = [a for a in agencies if a.status == 'suspended']
    for a in agencies:
        _attach_agency(a, request.session)

    if request.method == 'POST':
        action = request.POST.get('action') or request.POST.get('bulk_action')
        agency_ids = request.POST.getlist('selected_agencies') or request.POST.getlist('agency_ids')
        if action and agency_ids:
            applied = 0
            for aid in agency_ids:
                try:
                    agency = AgencyProfile.objects.get(pk=aid)
                except AgencyProfile.DoesNotExist:
                    continue
                if action == 'approve':
                    agency.status = 'approved'
                    agency.save()
                elif action == 'blacklist':
                    agency.status = 'suspended'
                    agency.save()
                elif action == 'unblacklist':
                    agency.status = 'approved'
                    agency.save()
                else:
                    continue
                applied += 1
                AuditLog.objects.create(
                    user=request.user, action=f'agency_{action}',
                    resource=f'agency:{aid}',
                    details=f'Action {action} on {agency.agency_name}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            messages.success(request, f'Action "{action}" applied to {applied} agency(ies).')
            return redirect('admin_portal:agencies')

    return render(request, 'admin_portal/agencies.html', {
        'agencies': agencies, 'query': query, 'total': len(agencies), 'status_filter': status_filter
    })


@login_required
@admin_required
def agency_detail(request, pk):
    agency = get_object_or_404(AgencyProfile.objects.select_related('user'), pk=pk)
    _attach_agency(agency, request.session)

    buses = [_attach_bus(b) for b in Bus.objects.filter(agency=agency.user).select_related('bus_type')]

    bookings = [
        _attach_booking(b) for b in Booking.objects
        .filter(schedule__bus__agency=agency.user_id)
        .select_related('passenger', 'schedule__bus', 'schedule__route')
        .order_by('-booking_date')[:20]
    ]

    drivers = []

    kyc_documents = []
    for field_name in ['gst_number', 'pan_number', 'aadhaar_number', 'registration_number']:
        val = getattr(agency, field_name, None)
        if val:
            kyc_documents.append({'name': field_name.replace('_', ' ').title(), 'detail': val, 'status': 'Provided'})

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            agency.status = 'approved'
            agency.save()
            messages.success(request, f'{agency.agency_name} approved.')
        elif action == 'blacklist':
            agency.status = 'suspended'
            agency.save()
            messages.success(request, f'{agency.agency_name} blacklisted.')
        elif action == 'unblacklist':
            agency.status = 'approved'
            agency.save()
            messages.success(request, f'{agency.agency_name} unblacklisted.')
        elif action == 'set_commission':
            try:
                rate = float(request.POST.get('commission_rate', DEFAULT_COMMISSION_RATE))
            except (TypeError, ValueError):
                rate = DEFAULT_COMMISSION_RATE
            request.session['commission_rate'] = rate
            messages.success(request, f'Platform commission rate updated to {rate}%.')
        AuditLog.objects.create(
            user=request.user, action=f'agency_{action}',
            resource=f'agency:{pk}',
            details=f'Action {action} on {agency.agency_name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return redirect('admin_portal:agency_detail', pk=pk)

    return render(request, 'admin_portal/agency_detail.html', {
        'agency': agency, 'buses': buses, 'bookings': bookings,
        'drivers': drivers, 'kyc_documents': kyc_documents
    })


@login_required
@admin_required
def manage_buses(request):
    buses = [_attach_bus(b) for b in Bus.objects.select_related('agency', 'bus_type').prefetch_related('schedules__route')]
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    if query:
        q = query.lower()
        buses = [b for b in buses if q in b.bus_number.lower() or q in (b.bus_name or '').lower()]
    if status_filter:
        status_map = {'active': 'active', 'inactive': 'inactive', 'pending': 'maintenance', 'rejected': 'inactive'}
        mapped = status_map.get(status_filter)
        if mapped:
            buses = [b for b in buses if b.status == mapped]

    if request.method == 'POST':
        action = request.POST.get('action') or request.POST.get('bulk_action')
        bus_ids = request.POST.getlist('selected_buses') or request.POST.getlist('bus_ids')
        if action and bus_ids:
            applied = 0
            for bid in bus_ids:
                try:
                    bus = Bus.objects.get(pk=bid)
                except Bus.DoesNotExist:
                    continue
                if action == 'approve':
                    bus.status = 'active'
                    bus.save()
                elif action == 'reject':
                    bus.status = 'inactive'
                    bus.save()
                else:
                    continue
                applied += 1
                AuditLog.objects.create(
                    user=request.user, action=f'bus_{action}',
                    resource=f'bus:{bid}',
                    details=f'Action {action} on {bus.bus_number}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            if action in ('feature', 'premium'):
                messages.info(request, f'"{action}" buses are not supported on the live schema yet.')
            messages.success(request, f'Action "{action}" applied to {applied} bus(es).')
            return redirect('admin_portal:buses')

    return render(request, 'admin_portal/buses.html', {
        'buses': buses, 'query': query, 'total': len(buses), 'status_filter': status_filter
    })


@login_required
@admin_required
def manage_cities(request):
    routes = list(Route.objects.annotate(stops_count=Count('stops')).order_by('origin', 'destination'))

    origin_counts = Counter(r.origin for r in routes)
    dest_counts = Counter(r.destination for r in routes)
    cities = []
    for name in sorted(set(origin_counts) | set(dest_counts)):
        departures = origin_counts.get(name, 0)
        arrivals = dest_counts.get(name, 0)
        cities.append({
            'name': name,
            'state': '',
            'is_popular': (departures + arrivals) > 1,
            'departures': departures,
            'arrivals': arrivals,
        })

    if request.method == 'POST':
        action = request.POST.get('action', 'add_city')
        if action in ('add_city', 'delete_city'):
            messages.info(request, 'Cities are derived automatically from active bus routes.')
            return redirect('admin_portal:cities')

    return render(request, 'admin_portal/cities.html', {
        'cities': cities, 'routes': routes,
        'total_cities': len(cities), 'total_routes': len(routes)
    })


@login_required
@admin_required
def manage_offers(request):
    coupons = [_attach_offer(o) for o in Offer.objects.all().order_by('-created_at')]
    referrals = User.objects.filter(user_type='passenger').count()
    festival_campaigns = FestivalCampaign.objects.all()
    flash_sales = FlashSale.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action', 'add_coupon')
        if action == 'add_coupon':
            code = request.POST.get('code', '').strip().upper()
            discount_type = request.POST.get('discount_type', 'percentage')
            try:
                discount_value = float(request.POST.get('discount_value', 0) or 0)
                min_amount = float(request.POST.get('min_amount', 0) or 0)
            except (TypeError, ValueError):
                discount_value = 0
                min_amount = 0
            if code and discount_value > 0:
                Offer.objects.get_or_create(
                    code=code,
                    defaults={
                        'title': f'Coupon {code}',
                        'offer_type': 'percent' if discount_type == 'percentage' else 'flat',
                        'discount_value': discount_value,
                        'min_booking_amount': min_amount,
                        'max_discount': 0,
                        'description': 'Created from the admin offers panel.',
                        'tagline': '',
                        'valid_from': timezone.now(),
                        'valid_until': timezone.now() + timedelta(days=30),
                        'is_active': True,
                    }
                )
                messages.success(request, f'Offer "{code}" created.')
                return redirect('admin_portal:offers')
        elif action == 'add_campaign':
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            try:
                discount = float(request.POST.get('discount_percent', 0) or 0)
            except (TypeError, ValueError):
                discount = 0
            coupon_code = request.POST.get('coupon_code', '').strip()
            start = request.POST.get('start_date')
            end = request.POST.get('end_date')
            if title and start and end:
                FestivalCampaign.objects.create(
                    title=title, description=description,
                    discount_percent=discount, coupon_code=coupon_code,
                    start_date=start, end_date=end
                )
                messages.success(request, f'Campaign "{title}" created.')
                return redirect('admin_portal:offers')
        elif action == 'add_flash':
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            try:
                discount = float(request.POST.get('flash_discount', 0) or 0)
            except (TypeError, ValueError):
                discount = 0
            coupon_code = request.POST.get('flash_coupon', '').strip()
            try:
                max_uses = int(request.POST.get('flash_max_uses', 100) or 100)
            except (TypeError, ValueError):
                max_uses = 100
            if title:
                FlashSale.objects.create(
                    title=title, description=description,
                    discount_percent=discount, coupon_code=coupon_code,
                    start_date=timezone.now(),
                    end_date=timezone.now() + timedelta(days=7),
                    max_uses=max_uses
                )
                messages.success(request, f'Flash sale "{title}" created.')
                return redirect('admin_portal:offers')

    return render(request, 'admin_portal/offers.html', {
        'coupons': coupons, 'referral_count': referrals,
        'festival_campaigns': festival_campaigns, 'flash_sales': flash_sales
    })


@login_required
@admin_required
def manage_payments(request):
    payments = Payment.objects.select_related('user', 'booking').order_by('-created_at')[:100]
    refunds = Refund.objects.select_related('payment__booking', 'payment__user').order_by('-created_at')[:100]
    for r in refunds:
        r.booking = r.payment.booking

    total_settled = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    total_refunded = Refund.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0

    try:
        commission_rate = float(request.session.get('commission_rate') or DEFAULT_COMMISSION_RATE)
    except (TypeError, ValueError):
        commission_rate = DEFAULT_COMMISSION_RATE

    commission_data = []
    for ap in AgencyProfile.objects.filter(status='approved').select_related('user'):
        agency_user = ap.user_id
        bc = Booking.objects.filter(schedule__bus__agency=agency_user).count()
        gross = Payment.objects.filter(
            status='completed', booking__schedule__bus__agency=agency_user
        ).aggregate(total=Sum('amount'))['total'] or 0
        rate = commission_rate
        earned = round(float(gross) * rate / 100, 2)
        commission_data.append({
            'agency_name': ap.agency_name,
            'commission_rate': rate,
            'booking_count': bc,
            'gross_revenue': round(float(gross), 2),
            'commission_earned': earned,
        })

    settlements = []
    for c in commission_data:
        gross = c['gross_revenue']
        commission = float(gross) * float(c['commission_rate'] or DEFAULT_COMMISSION_RATE) / 100
        settlements.append({
            'agency_name': c['agency_name'],
            'period': 'This Month',
            'booking_count': c['booking_count'],
            'gross_amount': gross,
            'commission_amount': round(commission, 2),
            'net_amount': round(float(gross) - commission, 2),
            'status': 'pending',
        })

    gst_taxable = float(total_settled)
    gst_records = []
    if gst_taxable > 0:
        gst_records.append({
            'period': timezone.now().strftime('%B %Y'),
            'taxable_amount': round(gst_taxable, 2),
            'cgst': round(gst_taxable * 0.09, 2),
            'sgst': round(gst_taxable * 0.09, 2),
            'total_gst': round(gst_taxable * 0.18, 2),
            'is_filed': False,
        })

    return render(request, 'admin_portal/payments.html', {
        'payments': payments, 'refunds': refunds,
        'total_settled': total_settled, 'total_refunded': total_refunded,
        'settlements': settlements, 'commissions': commission_data,
        'gst_records': gst_records
    })


@login_required
@admin_required
def support_center(request):
    tickets = SupportTicket.objects.select_related('user').order_by('-created_at')
    complaints = tickets.filter(category__in=['booking', 'payment', 'bus_quality', 'driver'])
    refund_requests = Refund.objects.select_related('payment__booking', 'payment__user').order_by('-created_at')
    for r in refund_requests:
        r.booking = r.payment.booking
    emergency_alerts = EmergencyAlert.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'resolve':
            tid = request.POST.get('complaint_id') or request.POST.get('ticket_id')
            if tid:
                SupportTicket.objects.filter(pk=tid).update(status='resolved')
                messages.success(request, 'Ticket resolved.')
        elif action == 'escalate':
            tid = request.POST.get('complaint_id') or request.POST.get('ticket_id')
            if tid:
                SupportTicket.objects.filter(pk=tid).update(status='in_progress', priority='high')
                messages.success(request, 'Ticket escalated.')
        elif action == 'refund':
            tid = request.POST.get('complaint_id')
            if tid:
                ticket = SupportTicket.objects.filter(pk=tid).first()
                if ticket and ticket.booking_id:
                    last_payment = ticket.booking.payments.filter(status='completed').first()
                    if last_payment:
                        Refund.objects.get_or_create(
                            payment=last_payment,
                            defaults={'amount': ticket.booking.final_amount, 'reason': ticket.subject}
                        )
                        messages.success(request, 'Refund initiated.')
        elif action == 'approve_refund':
            rid = request.POST.get('refund_id')
            if rid:
                Refund.objects.filter(pk=rid).update(status='completed')
                messages.success(request, 'Refund approved.')
        elif action == 'resolve_emergency':
            eid = request.POST.get('emergency_id')
            if eid:
                EmergencyAlert.objects.filter(pk=eid).update(is_resolved=True)
                messages.success(request, 'Emergency resolved.')
        return redirect('admin_portal:support')

    return render(request, 'admin_portal/support.html', {
        'tickets': tickets, 'complaints': complaints,
        'refund_requests': refund_requests, 'emergency_alerts': emergency_alerts
    })


@login_required
@admin_required
def manage_notifications(request):
    notifications = MassNotification.objects.all().order_by('-created_at')

    if request.method == 'POST':
        action = request.POST.get('action', 'send')
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        ntype = request.POST.get('type', '')
        target = request.POST.get('target_role', 'all')
        type_map = {
            'send_email': 'email', 'send_sms': 'sms',
            'send_push': 'push', 'send_announcement': 'announcement',
        }
        if not ntype:
            ntype = type_map.get(action, 'email')
        if title and message:
            MassNotification.objects.create(
                title=title, message=message, type=ntype,
                target_role=target, created_by=request.user
            )
            AuditLog.objects.create(
                user=request.user, action='send_notification',
                resource='notifications',
                details=f'Sent {ntype} to {target}: {title}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f'{ntype.title()} notification queued.')
            return redirect('admin_portal:notifications')

    return render(request, 'admin_portal/notifications.html', {'notifications': notifications})


@login_required
@admin_required
def cms(request):
    banners = Banner.objects.all()
    blogs = BlogPost.objects.all()
    faqs = FAQ.objects.all()
    offer_pages = Offer.objects.filter(is_active=True)

    privacy = PageContent.objects.filter(slug='privacy').first()
    terms = PageContent.objects.filter(slug='terms').first()

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'add_banner':
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            link = request.POST.get('link', '').strip()
            if title:
                Banner.objects.create(title=title, description=description, link=link)
                messages.success(request, 'Banner created.')
                return redirect('admin_portal:cms')
        elif action == 'add_blog':
            title = request.POST.get('title', '').strip()
            slug = request.POST.get('slug', '').strip()
            content = request.POST.get('content', '').strip()
            if title and slug:
                BlogPost.objects.create(title=title, slug=slug, content=content)
                messages.success(request, 'Blog post created.')
                return redirect('admin_portal:cms')
        elif action == 'add_faq':
            question = request.POST.get('question', '').strip()
            answer = request.POST.get('answer', '').strip()
            if question and answer:
                FAQ.objects.create(question=question, answer=answer)
                messages.success(request, 'FAQ added.')
                return redirect('admin_portal:cms')
        elif action in ('save_privacy', 'save_terms'):
            content = request.POST.get('content', '')
            slug = 'privacy' if action == 'save_privacy' else 'terms'
            title = 'Privacy Policy' if slug == 'privacy' else 'Terms of Service'
            obj, _ = PageContent.objects.get_or_create(slug=slug, defaults={'title': title})
            obj.content = content
            obj.save()
            messages.success(request, f'{title} updated.')
            return redirect('admin_portal:cms')

    return render(request, 'admin_portal/cms.html', {
        'banners': banners, 'blogs': blogs, 'faqs': faqs, 'offer_pages': offer_pages,
        'privacy_content': privacy.content if privacy else '',
        'terms_content': terms.content if terms else '',
    })


@login_required
@admin_required
def reports(request):
    today = timezone.now().date()
    period = request.GET.get('period', 'daily')
    if period == 'monthly':
        start = today - timedelta(days=30)
    elif period == 'yearly':
        start = today - timedelta(days=365)
    else:
        start = today

    total_revenue = Payment.objects.filter(status='completed', paid_at__date__gte=start).aggregate(total=Sum('amount'))['total'] or 0
    total_bookings_count = Booking.objects.filter(booking_date__gte=start).count()
    avg_booking_value = round(float(total_revenue) / total_bookings_count, 2) if total_bookings_count else 0
    active_users = User.objects.filter(user_type='passenger', is_active=True).count()
    total_refunds = Refund.objects.filter(created_at__date__gte=start, status='completed').aggregate(total=Sum('amount'))['total'] or 0
    refund_rate = round((float(total_refunds) / float(total_revenue) * 100), 1) if total_revenue else 0

    daily_revenue = list(
        Payment.objects.filter(status='completed', paid_at__date__gte=start)
        .values('paid_at__date').annotate(
            total=Sum('amount'), count=Count('id')
        ).order_by('paid_at__date')
    )
    enriched_revenue = []
    for row in daily_revenue:
        d = row['paid_at__date']
        refunds = Refund.objects.filter(created_at__date=d, status='completed').aggregate(total=Sum('amount'))['total'] or 0
        gross = float(row['total'])
        enriched_revenue.append({
            'date': d,
            'gross_revenue': round(gross, 2),
            'commission': round(gross * 0.10, 2),
            'refunds': round(float(refunds), 2),
            'net_revenue': round(gross - gross * 0.10 - float(refunds), 2),
            'booking_count': row['count'],
        })

    daily_bookings = []
    for row in (
        Booking.objects.filter(booking_date__gte=start)
        .values('booking_date').annotate(
            total=Count('id'),
            confirmed=Count('id', filter=Q(status='confirmed')),
            cancelled=Count('id', filter=Q(status='cancelled')),
        ).order_by('booking_date')
    ):
        row['date'] = row.pop('booking_date')
        row['refunded'] = 0
        row['occupancy_rate'] = 0
        daily_bookings.append(row)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'export_csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="gobus_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['Date', 'Revenue', 'Bookings'])
            for row in enriched_revenue:
                writer.writerow([row['date'], row['gross_revenue'], row['booking_count']])
            return response
        elif action == 'export_excel':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="gobus_report.xls"'
            writer = csv.writer(response, delimiter='\t')
            writer.writerow(['Date', 'Gross Revenue', 'Commission', 'Refunds', 'Net Revenue', 'Bookings'])
            for row in enriched_revenue:
                writer.writerow([row['date'], row['gross_revenue'], row['commission'], row['refunds'], row['net_revenue'], row['booking_count']])
            return response
        elif action == 'export_pdf':
            lines = ['GoBus Report', f'Period: {period.title()}', f'From: {start} To: {today}', '']
            lines.append(f'Total Revenue: Rs.{total_revenue}')
            lines.append(f'Total Bookings: {total_bookings_count}')
            lines.append(f'Avg Booking Value: Rs.{avg_booking_value}')
            lines.append(f'Refund Rate: {refund_rate}%')
            lines.append('')
            for row in enriched_revenue:
                lines.append(f"{row['date']} | Rs.{row['gross_revenue']} | {row['booking_count']} bookings")
            response = HttpResponse('\n'.join(lines), content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="gobus_report.txt"'
            return response

    return render(request, 'admin_portal/reports.html', {
        'daily_revenue': enriched_revenue, 'daily_bookings': daily_bookings,
        'period': period, 'start': start,
        'total_revenue': total_revenue, 'total_bookings': total_bookings_count,
        'avg_booking_value': avg_booking_value, 'active_users': active_users,
        'refund_rate': refund_rate
    })


@login_required
@admin_required
def security(request):
    login_logs = LoginLog.objects.all()[:100]
    failed_logins = FailedLogin.objects.all()[:50]
    whitelisted_ips = IPRecord.objects.filter(list_type='whitelist')
    blacklisted_ips = IPRecord.objects.filter(list_type='blacklist')
    audit_logs = AuditLog.objects.all()[:100]
    all_users = User.objects.filter(user_type='admin')

    security_alerts = FailedLogin.objects.filter(is_locked=True)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_whitelist':
            ip = request.POST.get('ip_address', '').strip()
            if ip:
                IPRecord.objects.get_or_create(address=ip, list_type='whitelist',
                    defaults={'label': request.POST.get('label', '')})
                messages.success(request, f'IP {ip} whitelisted.')
        elif action == 'add_blacklist':
            ip = request.POST.get('ip_address', '').strip()
            reason = request.POST.get('reason', '').strip()
            if ip:
                IPRecord.objects.get_or_create(address=ip, list_type='blacklist',
                    defaults={'reason': reason})
                messages.success(request, f'IP {ip} blacklisted.')
        elif action == 'remove_whitelist':
            ip = request.POST.get('ip')
            IPRecord.objects.filter(address=ip, list_type='whitelist').delete()
            messages.success(request, f'IP {ip} removed from whitelist.')
        elif action == 'remove_blacklist':
            ip = request.POST.get('ip')
            IPRecord.objects.filter(address=ip, list_type='blacklist').delete()
            messages.success(request, f'IP {ip} removed from blacklist.')
        elif action == 'clear_failed':
            FailedLogin.objects.all().delete()
            messages.success(request, 'Failed login records cleared.')
        elif action == 'clear_audit':
            AuditLog.objects.all().delete()
            messages.success(request, 'Audit logs cleared.')
        AuditLog.objects.create(
            user=request.user, action=f'security_{action}',
            resource='security',
            details=f'Security action: {action}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return redirect('admin_portal:security')

    return render(request, 'admin_portal/security.html', {
        'sessions': login_logs,
        'failed_logins': failed_logins,
        'whitelisted_ips': whitelisted_ips,
        'blacklisted_ips': blacklisted_ips,
        'audit_logs': audit_logs,
        'all_users': all_users,
        'security_alerts': security_alerts,
        'users_with_2fa': 0,
        'users_without_2fa': all_users.count(),
    })