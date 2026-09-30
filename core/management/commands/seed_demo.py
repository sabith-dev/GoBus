from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import AgencyProfile, PassengerProfile
from buses.models import BusType, Bus, Seat
from routes.models import Route, RouteStop
from schedules.models import Schedule
from bookings.models import Booking
from reviews.models import Review
from offers.models import Offer
from core.models import FAQ

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed GoBus with realistic demo data (bus types, agency, buses, routes, schedules, offers, FAQs)'

    def handle(self, *args, **options):
        # Bus types
        bus_types = [
            ('AC Seater', 23, True, False, ['AC', 'Reclining seats', 'Reading light', 'Mobile charging']),
            ('AC Sleeper', 17, True, True, ['AC', 'Sleepers', 'Reading light', 'Blanket']),
            ('Volvo Multi-Axle AC Sleeper', 35, True, True, ['AC', 'Sleepers', 'WiFi', 'Charging', 'Water']),
            ('Non-AC', 40, False, False, ['Standard seats']),
            ('Semi Sleeper', 29, True, False, ['AC', 'Semi sleeper', 'Charging']),
            ('Luxury AC Seater', 23, True, False, ['AC', 'Pushback seats', 'WiFi', 'Snacks']),
            ('Sleeper', 24, False, True, ['Sleepers', 'Reading light']),
            ('Electric Bus', 30, True, False, ['AC', 'Charging', 'Eco friendly']),
        ]
        for name, seats, is_ac, is_sleeper, amens in bus_types:
            BusType.objects.get_or_create(name=name, defaults={
                'total_seats': seats, 'is_ac': is_ac, 'is_sleeper': is_sleeper, 'amenities': amens,
            })

        # Admin / demo users
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(username='admin', email='admin@gobus.com', password='admin123')
        User.objects.filter(username='admin').update(user_type='admin')
        if not User.objects.filter(username='keralatravels').exists():
            agency_user = User.objects.create_user(
                username='keralatravels', email='partner@keralatravels.com',
                password='agency123', user_type='agency')
            AgencyProfile.objects.get_or_create(
                user=agency_user,
                defaults={
                    'agency_name': 'Kerala Travels',
                    'agency_code': 'AG00001',
                    'status': 'approved',
                    'is_verified': True,
                    'city': 'Kochi',
                    'state': 'Kerala',
                    'contact_phone': '+919876543210',
                })
        if not User.objects.filter(username='rahul').exists():
            passenger_user = User.objects.create_user(
                username='rahul', email='rahul@example.com',
                password='passenger123', user_type='passenger')
            PassengerProfile.objects.get_or_create(user=passenger_user)

        agency_user = User.objects.filter(user_type='agency').first()
        passenger_user = User.objects.filter(user_type='passenger').first()

        # Buses
        buses = [
            ('KL-01-AB-1234', 'Kerala Express', 'Volvo Multi-Axle AC Sleeper'),
            ('KL-07-CD-5678', 'Malabar Super Fast', 'AC Sleeper'),
            ('KA-05-EF-9001', 'Bangalore Star', 'Luxury AC Seater'),
            ('MH-12-GH-3456', 'Mumbai Rocket', 'AC Seater'),
            ('DL-01-JK-7890', 'Rajdhani Travels', 'Semi Sleeper'),
            ('TN-09-LM-1122', 'Chennai Connect', 'Non-AC'),
            ('KA-03-NP-3344', 'Deccan Queen', 'Sleeper'),
            ('KL-02-QR-5566', 'Gods Own Express', 'Electric Bus'),
        ]
        created_buses = []
        for reg, name, btype in buses:
            bt = BusType.objects.filter(name=btype).first()
            bus, created = Bus.objects.get_or_create(bus_number=reg, defaults={
                'agency': agency_user, 'bus_type': bt, 'bus_name': name,
                'total_seats': bt.total_seats,
                'seat_layout': {'rows': bt.total_seats // 2 if bt.total_seats % 2 == 0 else bt.total_seats // 2},
                'image': None, 'status': 'active',
            })
            if created:
                for i in range(1, bt.total_seats + 1):
                    row = (i - 1) // 2 + 1
                    col = (i - 1) % 2 + 1
                    Seat.objects.create(
                        bus=bus, seat_number=f'{i:02d}',
                        seat_type='sleeper' if bt.is_sleeper else 'seater',
                        deck=1, row=row, column=col,
                        is_window=col == 1, is_available=True,
                    )
            created_buses.append(bus)

        # Routes
        routes = [
            ('Kochi', 'Bangalore', 480, '9:00:00', 799),
            ('Kochi', 'Chennai', 680, '11:00:00', 999),
            ('Bangalore', 'Hyderabad', 570, '9:30:00', 749),
            ('Chennai', 'Bangalore', 350, '6:30:00', 499),
            ('Mumbai', 'Pune', 150, '3:00:00', 249),
            ('Delhi', 'Jaipur', 280, '5:30:00', 399),
            ('Bangalore', 'Mysore', 140, '3:00:00', 249),
            ('Kochi', 'Trivandrum', 220, '4:30:00', 299),
        ]
        created_routes = []
        for orig, dest, dist, dur, fare in routes:
            route, created = Route.objects.get_or_create(
                agency=agency_user, origin=orig, destination=dest,
                defaults={
                    'name': f'{orig} to {dest}',
                    'distance_km': dist,
                    'estimated_duration': timedelta(hours=int(dur.split(':')[0]), minutes=int(dur.split(':')[1])),
                    'base_fare': fare,
                })
            if created:
                RouteStop.objects.get_or_create(route=route, sequence=1, name=orig, city=orig,
                                                arrival_offset=timedelta(0), departure_offset=timedelta(0))
                RouteStop.objects.get_or_create(route=route, sequence=2, name=dest, city=dest,
                                                arrival_offset=timedelta(hours=int(dur.split(':')[0])),
                                                departure_offset=timedelta(hours=int(dur.split(':')[0])))
            created_routes.append(route)

        # Schedules
        times = ['06:30', '09:00', '14:30', '18:00', '21:30', '23:00']
        for i, route in enumerate(created_routes[:8]):
            bus = created_buses[i % len(created_buses)]
            dep = times[i % len(times)]
            h, m = map(int, dep.split(':'))
            dep_t = timezone.now().time().replace(hour=h, minute=m, second=0, microsecond=0)
            arr_secs = ((h * 3600 + m * 60) + int(route.estimated_duration.total_seconds())) % 86400
            arr_t = timezone.now().time().replace(hour=arr_secs // 3600, minute=(arr_secs % 3600) // 60, second=0, microsecond=0)
            Schedule.objects.get_or_create(
                bus=bus, route=route, departure_time=dep_t, arrival_time=arr_t,
                defaults={
                    'fare': route.base_fare,
                    'operating_days': [0, 1, 2, 3, 4, 5, 6],
                    'effective_from': date.today() - timedelta(days=30),
                    'is_active': True,
                })

        # Offers
        today = date.today()
        offers = [
            ('FIRST RIDE', 'First Ride', 'flat', 150, 499, None, 'Get ₹150 OFF on your first booking', 'fa-gift'),
            ('WEEKEND', 'Weekend Deals', 'percent', 10, 799, 200, '10% off on weekend travel', 'fa-moon'),
            ('STUDENT', 'Student Offers', 'percent', 15, 599, 150, '15% off for verified students', 'fa-graduation-cap'),
            ('EARLYBIRD', 'Early Booking', 'flat', 200, 999, None, 'Book 7 days early and save', 'fa-bell'),
            ('ROUTEOFF', 'Route Offers', 'percent', 12, 699, 180, '12% off on popular routes', 'fa-route'),
            ('FESTIVE', 'Festive Special', 'percent', 20, 999, 300, '20% off during the festive season', 'fa-fire'),
        ]
        for title, tag, otype, val, minamt, maxdisc, desc, icon in offers:
            Offer.objects.get_or_create(code=title, defaults={
                'title': title.title().replace(' Ride', ' Ride'), 'tagline': tag,
                'offer_type': otype, 'discount_value': val, 'min_booking_amount': minamt,
                'max_discount': maxdisc, 'description': desc, 'icon': icon,
                'valid_from': today - timedelta(days=10), 'valid_until': today + timedelta(days=60),
                'is_active': True,
            })

        # FAQs
        faqs = [
            ('How do I book a bus?', 'Search your route, choose a bus, pick your seat and complete the secure payment. Your e-ticket is generated instantly.'),
            ('How can I cancel my ticket?', 'Go to My Bookings, select the trip and click Cancel. The refund is calculated automatically based on the cancellation policy.'),
            ('Can I choose my seat?', 'Yes. During booking you will see a live seat map and can choose any available seat.'),
            ('How do I download my ticket?', 'Your ticket is available in My Bookings and the confirmation email. You can also download it as a QR e-ticket.'),
            ('Can I track my bus?', 'Yes. Tracking is available for live-trackable buses during the travel window.'),
            ('How does refund work?', 'Refunds are processed to your original payment method or GoBus wallet, usually within 5-7 working days.'),
            ('Are payments secure?', 'Absolutely. All transactions are encrypted and processed through PCI-compliant payment gateways.'),
            ('Can I change my travel date?', 'Date changes depend on the operator policy. Some tickets can be rescheduled with a small fee.'),
        ]
        for q, a in faqs:
            FAQ.objects.get_or_create(question=q, defaults={'answer': a})

        # Testimonials (need completed bookings + approved reviews)
        if Review.objects.count() == 0 and passenger_user:
            testimonials = [
                ('Super comfortable bus, on-time departure and the app tracking was spot on. Highly recommended!', 5, 'Arjun', 'Kerala Express'),
                ('Clean seats, free WiFi and the booking process took under a minute. Love the upfront pricing.', 4, 'Priya', 'Bangalore Star'),
                ('The sleeper bus was great for the overnight ride. AC worked perfectly and blankets provided.', 5, 'Divya', 'Malabar Super Fast'),
                ('Booked in a hurry, got my e-ticket instantly. The seat selection map made it so easy.', 4, 'Imran', 'Mumbai Rocket'),
            ]
            schedules = list(Schedule.objects.select_related('bus', 'route')[:])
            for idx, (comment, rating, first, bus_name) in enumerate(testimonials):
                sched = schedules[idx % len(schedules)]
                passenger_name = first
                booking = Booking.objects.create(
                    passenger=passenger_user,
                    schedule=sched,
                    travel_date=date.today() - timedelta(days=20 + idx),
                    status='completed',
                    total_amount=sched.fare,
                    discount_amount=0,
                    final_amount=sched.fare,
                    passenger_name=passenger_name,
                    passenger_email=passenger_user.email,
                    passenger_phone='+919876543210',
                )
                Review.objects.create(
                    booking=booking,
                    user=passenger_user,
                    bus=sched.bus,
                    rating=rating,
                    title=f'{first} travelled {sched.route.origin} to {sched.route.destination}',
                    comment=comment,
                    cleanliness_rating=rating,
                    punctuality_rating=rating,
                    comfort_rating=rating,
                    is_approved=True,
                )

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete: {BusType.objects.count()} bus types, {Bus.objects.count()} buses, '
            f'{Route.objects.count()} routes, {Schedule.objects.count()} schedules, '
            f'{Offer.objects.count()} offers, {FAQ.objects.count()} FAQs, '
            f'{Review.objects.count()} testimonials.'))