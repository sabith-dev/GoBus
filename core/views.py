from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Min, Q
from .models import FAQ, SiteSetting
from .forms import ContactForm
from offers.models import Offer
from reviews.models import Review
from routes.models import Route
from schedules.models import Schedule
from buses.models import BusType


def _popular_routes(limit=6):
    routes = []
    qs = (
        Schedule.objects
        .filter(route__is_active=True, is_active=True, bus__status='active')
        .values('route_id', 'route__origin', 'route__destination')
        .annotate(starting_fare=Min('fare'))
        .order_by('-route_id')[:limit]
    )
    for item in qs:
        routes.append({
            'id': item['route_id'],
            'origin': item['route__origin'],
            'destination': item['route__destination'],
            'starting_fare': item['starting_fare'],
        })
    return routes


def home_view(request):
    today = datetime.today()
    context = {
        'popular_routes': _popular_routes(),
        'offers': Offer.objects.filter(is_active=True, valid_until__gte=today.date()).order_by('-created_at')[:4],
        'bus_categories': BusType.objects.all().order_by('name')[:8],
        'testimonials': Review.objects.filter(is_approved=True).order_by('-created_at')[:5],
        'faqs': FAQ.objects.filter(is_active=True)[:6],
        'from_city': request.GET.get('from', ''),
        'to_city': request.GET.get('to', ''),
        'trip_date': request.GET.get('date', ''),
        'trip_type': request.GET.get('trip_type', 'oneway'),
    }
    return render(request, 'public/home.html', context)


def about_view(request):
    return render(request, 'public/about.html', {
        'stats': {
            'routes': Route.objects.filter(is_active=True).count(),
            'agencies': 1200,
            'travellers': 10000000,
            'cities': 300,
        }
    })


def features_view(request):
    return render(request, 'public/features.html')


def offers_view(request):
    today = datetime.today().date()
    return render(request, 'public/offers.html', {
        'offers': Offer.objects.filter(is_active=True, valid_until__gte=today).order_by('-created_at'),
    })


def faq_view(request):
    return render(request, 'public/faq.html', {
        'faqs': FAQ.objects.filter(is_active=True),
    })


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you! Your message has been sent. We will get back to you soon.')
            return redirect('core:contact')
    else:
        form = ContactForm()
    return render(request, 'public/contact.html', {
        'form': form,
        'app_phone': SiteSetting.get('contact_phone', '1800-XXX-XXXX'),
        'app_email': SiteSetting.get('contact_email', 'support@gobus.com'),
    })


def search_view(request):
    origin = request.GET.get('from', '').strip()
    destination = request.GET.get('to', '').strip()
    trip_date = request.GET.get('date', '').strip()
    trip_type = request.GET.get('trip_type', 'oneway')
    bus_type = request.GET.get('bus_type', '')

    results = Schedule.objects.filter(route__is_active=True, is_active=True, bus__status='active')
    if origin:
        results = results.filter(Q(route__origin__icontains=origin) | Q(route__origin__icontains=origin.lower()))
    if destination:
        results = results.filter(route__destination__icontains=destination)
    if bus_type:
        results = results.filter(bus__bus_type__name__icontains=bus_type)

    results = results.select_related('bus', 'bus__bus_type', 'route', 'route__agency').distinct().order_by('departure_time')[:20]

    parsed_date = None
    if trip_date:
        try:
            parsed_date = datetime.strptime(trip_date, '%Y-%m-%d').date()
        except ValueError:
            parsed_date = None

    day_filtered = []
    for s in results:
        if parsed_date is not None:
            weekday = parsed_date.weekday()
            if weekday not in s.operating_days:
                continue
        day_filtered.append(s)

    return render(request, 'public/search.html', {
        'results': day_filtered,
        'origin': origin,
        'destination': destination,
        'trip_date': trip_date,
        'trip_type': trip_type,
    })