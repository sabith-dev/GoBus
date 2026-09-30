import random
import uuid
from datetime import timedelta, date, time, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from accounts.models import CustomUser, UserProfile
from agencies.models import AgencyProfile, Driver
from buses.models import City, Route, BusType, Bus, Seat, BusSchedule, Amenity
from bookings.models import Booking, Passenger, Ticket
from payments.models import Payment, Coupon, Refund
from wallet.models import Wallet, WalletTransaction
from dashboard.models import (
    Banner, BlogPost, FAQ, PageContent,
    SupportTicket, EmergencyAlert,
    LoginLog, AuditLog, FestivalCampaign, FlashSale,
)
from notifications_app.models import Notification, MassNotification

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with realistic GoBus data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding GoBus database...')

        # ── Cities ──
        cities_data = [
            ('Mumbai', 'Maharashtra'), ('Pune', 'Maharashtra'),
            ('Delhi', 'Delhi'), ('Bangalore', 'Karnataka'),
            ('Chennai', 'Tamil Nadu'), ('Hyderabad', 'Telangana'),
            ('Ahmedabad', 'Gujarat'), ('Jaipur', 'Rajasthan'),
            ('Kolkata', 'West Bengal'), ('Goa', 'Goa'),
            ('Kochi', 'Kerala'), ('Lucknow', 'Uttar Pradesh'),
        ]
        cities = {}
        for name, state in cities_data:
            city, _ = City.objects.get_or_create(
                name=name, defaults={'state': state, 'is_popular': name in ('Mumbai', 'Delhi', 'Bangalore', 'Pune', 'Goa')}
            )
            cities[name] = city
        self.stdout.write(f'  Cities: {len(cities)}')

        # ── Routes ──
        routes_data = [
            ('Mumbai', 'Pune', 150, '2h 30m'), ('Mumbai', 'Delhi', 1400, '20h'),
            ('Mumbai', 'Goa', 580, '10h'), ('Mumbai', 'Ahmedabad', 530, '8h'),
            ('Pune', 'Bangalore', 840, '12h'), ('Pune', 'Goa', 450, '8h'),
            ('Delhi', 'Jaipur', 280, '5h'), ('Delhi', 'Lucknow', 550, '8h'),
            ('Delhi', 'Bangalore', 2100, '30h'), ('Bangalore', 'Chennai', 350, '6h'),
            ('Bangalore', 'Hyderabad', 570, '9h'), ('Chennai', 'Hyderabad', 800, '12h'),
            ('Hyderabad', 'Mumbai', 780, '12h'), ('Ahmedabad', 'Jaipur', 680, '10h'),
            ('Kolkata', 'Delhi', 1450, '20h'), ('Kochi', 'Bangalore', 600, '10h'),
            ('Goa', 'Bangalore', 580, '10h'),
        ]
        routes = {}
        for orig, dest, dist, dur in routes_data:
            hours, mins = int(dur.split('h')[0]), 0
            if 'm' in dur:
                mins = int(dur.split('h')[1].replace('m', '').strip())
            duration = timedelta(hours=hours, minutes=mins)
            route, _ = Route.objects.get_or_create(
                origin=cities[orig], destination=cities[dest],
                defaults={'distance_km': Decimal(str(dist)), 'expected_duration': duration}
            )
            routes[(orig, dest)] = route
        self.stdout.write(f'  Routes: {len(routes)}')

        # ── BusTypes ──
        bus_types = {}
        bt_data = [
            ('AC Sleeper', 40, True, True, True, True),
            ('AC Seater', 45, False, True, True, False),
            ('Non-AC Seater', 50, False, False, False, False),
            ('Volvo AC', 35, False, True, True, True),
            ('Semi Sleeper', 42, True, False, True, False),
        ]
        for name, seats, sleeper, ac, charging, wifi in bt_data:
            bt, _ = BusType.objects.get_or_create(
                name=name,
                defaults={
                    'total_seats': seats, 'is_sleeper': sleeper, 'is_ac': ac,
                    'has_charging_port': charging, 'has_wifi': wifi,
                    'has_blank': ac, 'has_water_bottle': ac,
                }
            )
            bus_types[name] = bt
        self.stdout.write(f'  BusTypes: {len(bus_types)}')

        # ── Amenities ──
        amenity_names = ['WiFi', 'Charging Port', 'Blank', 'Water Bottle', 'TV', 'GPS Tracking', 'CCTV']
        amenities = {}
        for name in amenity_names:
            a, _ = Amenity.objects.get_or_create(name=name)
            amenities[name] = a

        # ── Agencies ──
        agency_users_data = [
            ('neotransit', 'neo@transit.com', '9876543210', 'Neo Transit Co.', 'Mumbai', 'Maharashtra',
             411001, 'Premium bus operator serving Western and Southern India', '12.9716 77.5946'),
            ('royalroadways', 'royal@roadways.com', '9876543211', 'Royal Roadways Pvt Ltd', 'Delhi', 'Delhi',
             110001, 'Luxury coach services across North India', '28.7041 77.1025'),
            ('sunlinetravel', 'sunline@travel.com', '9876543212', 'Sunline Travel Services', 'Bangalore', 'Karnataka',
             560001, 'Reliable daily services in Karnataka and neighboring states', '12.9716 77.5946'),
            ('southernexpress', 'southern@express.com', '9876543213', 'Southern Express Lines', 'Chennai', 'Tamil Nadu',
             600001, 'Connecting South India with comfort and safety', '13.0827 80.2707'),
        ]
        agencies = {}
        for uname, email, phone, name, city, state, pin, desc, coords in agency_users_data:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    'email': email, 'phone': phone, 'role': 'agency',
                    'first_name': name.split()[0], 'last_name': ' '.join(name.split()[1:]),
                    'email_verified': True, 'is_active': True,
                }
            )
            if created:
                user.set_password('agency123')
                user.save()
            agency, _ = AgencyProfile.objects.get_or_create(
                user=user,
                defaults={
                    'agency_name': name, 'phone': phone, 'email': email,
                    'address': f'Head Office, {city}', 'city': city, 'state': state,
                    'pincode': str(pin), 'description': desc,
                    'is_approved': True, 'commission_rate': Decimal(str(random.choice([8, 10, 12, 15]))),
                    'rating': Decimal(str(round(random.uniform(3.5, 4.8), 1))),
                    'total_revenue': Decimal(str(random.randint(500000, 2500000))),
                    'gst_number': f'27AABCU9603R1ZM{random.randint(10,99)}',
                    'pan_number': f'AABCU9603R',
                    'registration_number': f'MH-AGC-{random.randint(1000,9999)}',
                }
            )
            agencies[uname] = agency
        self.stdout.write(f'  Agencies: {len(agencies)}')

        # ── Drivers ──
        driver_names = [
            ('Rajesh Kumar', '9876500001'), ('Suresh Patel', '9876500002'),
            ('Mohammed Ali', '9876500003'), ('Vikram Singh', '9876500004'),
            ('Anil Sharma', '9876500005'), ('Ravi Verma', '9876500006'),
            ('Deepak Nair', '9876500007'), ('Prakash Reddy', '9876500008'),
            ('Sanjay Mishra', '9876500009'), ('Vinod Gupta', '9876500010'),
            ('Ramesh Yadav', '9876500011'), ('Kumar Rajan', '9876500012'),
        ]
        agency_list = list(agencies.values())
        drivers = []
        for i, (dname, dphone) in enumerate(driver_names):
            agency = agency_list[i % len(agency_list)]
            driver, _ = Driver.objects.get_or_create(
                agency=agency, license_number=f'DL-{random.randint(10,99)}-{random.randint(100000,999999)}',
                defaults={
                    'name': dname, 'phone': dphone,
                    'license_expiry': date(2028, random.randint(1, 12), random.randint(1, 28)),
                    'experience_years': random.randint(3, 15),
                    'salary': Decimal(str(random.randint(20000, 45000))),
                    'is_on_duty': random.choice([True, False]),
                }
            )
            drivers.append(driver)
        self.stdout.write(f'  Drivers: {len(drivers)}')

        # ── Buses ──
        bus_names_pool = [
            'Volvo B9R Multi-Axle', 'Scania AC Sleeper', 'Mercedes-Benz O500',
            'Tata Marcopolo', 'Ashok Leyland Viking', 'Eicher Skyline',
            'BYD Electric Bus', 'Force Traveller', 'BharatBenz Tourer',
        ]
        route_list = list(routes.values())
        buses = []
        bus_counter = 1
        for agency in agency_list:
            num_buses = random.randint(4, 7)
            for _ in range(num_buses):
                route = random.choice(route_list)
                bt = random.choice(list(bus_types.values()))
                seats = bt.total_seats
                status = random.choice(['active', 'active', 'active', 'active', 'inactive', 'maintenance'])
                bus, _ = Bus.objects.get_or_create(
                    bus_number=f'MH-{random.randint(10,99)}-{bus_counter:04d}',
                    defaults={
                        'agency': agency, 'bus_type': bt, 'route': route,
                        'bus_name': random.choice(bus_names_pool),
                        'status': status, 'total_seats': seats,
                        'is_featured': random.random() < 0.2,
                        'is_premium': random.random() < 0.15,
                        'price_per_km': Decimal(str(round(random.uniform(1.5, 4.0), 2))),
                        'rating': Decimal(str(round(random.uniform(3.0, 5.0), 2))),
                    }
                )
                if bus.pk:
                    buses.append(bus)
                    bus_counter += 1
        self.stdout.write(f'  Buses: {len(buses)}')

        # ── Seats for each bus ──
        seat_counter = 0
        for bus in buses:
            if bus.seats.exists():
                continue
            seats_to_create = []
            bt = bus.bus_type
            total = bus.total_seats
            cols = 4 if bt.is_sleeper else 5
            for i in range(1, total + 1):
                row = (i - 1) // cols + 1
                col = (i - 1) % cols + 1
                deck = 'upper' if bt.is_sleeper and row > total // (cols * 2) else 'lower'
                stype = 'sleeper' if bt.is_sleeper else ('window' if col in (1, cols) else 'seater')
                seats_to_create.append(Seat(
                    bus=bus, seat_number=f'{row}{chr(64 + col)}',
                    row=row, column=col, deck=deck, seat_type=stype,
                ))
            Seat.objects.bulk_create(seats_to_create)
            seat_counter += len(seats_to_create)
        self.stdout.write(f'  Seats: {seat_counter}')

        # ── Bus Schedules ──
        schedule_counter = 0
        for bus in buses:
            if bus.schedules.exists():
                continue
            if not bus.route:
                continue
            dep_times = [
                time(random.choice([5, 6, 8, 10, 14, 18, 21, 23]), random.choice([0, 15, 30, 45]))
            ]
            for dt in dep_times:
                dur = bus.route.expected_duration or timedelta(hours=8)
                arr = (datetime.combine(date.today(), dt) + dur).time()
                days = random.choice([
                    [0,1,2,3,4,5,6], [0,2,4,6], [1,3,5], [0,1,2,3,4],
                ])
                price = Decimal(str(random.randint(300, 2500)))
                BusSchedule.objects.get_or_create(
                    bus=bus, departure_time=dt,
                    defaults={
                        'route': bus.route, 'arrival_time': arr,
                        'period': 'morning' if dt.hour < 12 else ('afternoon' if dt.hour < 17 else 'evening'),
                        'operating_days': days, 'base_price': price,
                    }
                )
                schedule_counter += 1
        self.stdout.write(f'  Schedules: {schedule_counter}')

        # ── Users ──
        users_data = [
            ('rahul_tripathi', 'rahul@gmail.com', '9000000001', 'Rahul', 'Tripathi', 'M'),
            ('priya_sharma', 'priya@gmail.com', '9000000002', 'Priya', 'Sharma', 'F'),
            ('amit_kumar', 'amit.k@gmail.com', '9000000003', 'Amit', 'Kumar', 'M'),
            ('sneha_patel', 'sneha@gmail.com', '9000000004', 'Sneha', 'Patel', 'F'),
            ('vikram_reddy', 'vikram.r@gmail.com', '9000000005', 'Vikram', 'Reddy', 'M'),
            ('deepa_nair', 'deepa.n@gmail.com', '9000000006', 'Deepa', 'Nair', 'F'),
            ('arjun_singh', 'arjun.s@gmail.com', '9000000007', 'Arjun', 'Singh', 'M'),
            ('meera_das', 'meera.d@gmail.com', '9000000008', 'Meera', 'Das', 'F'),
            ('karthik_menon', 'karthik.m@gmail.com', '9000000009', 'Karthik', 'Menon', 'M'),
            ('anjali_rao', 'anjali.r@gmail.com', '9000000010', 'Anjali', 'Rao', 'F'),
        ]
        users = {}
        for uname, email, phone, first, last, gender in users_data:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    'email': email, 'phone': phone, 'role': 'user',
                    'first_name': first, 'last_name': last,
                    'email_verified': random.choice([True, True, False]),
                    'is_active': True,
                }
            )
            if created:
                user.set_password('user123')
                user.save()
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'gender': gender, 'city': random.choice(list(cities.keys())[:6]),
                    'state': random.choice(['Maharashtra', 'Karnataka', 'Delhi', 'Tamil Nadu']),
                }
            )
            users[uname] = user
        self.stdout.write(f'  Users: {len(users)}')

        # ── Wallets ──
        for user in users.values():
            wallet, _ = Wallet.objects.get_or_create(
                user=user,
                defaults={
                    'balance': Decimal(str(random.randint(50, 2000))),
                    'reward_points': random.randint(0, 500),
                    'cashback': Decimal(str(random.randint(0, 200))),
                }
            )
        self.stdout.write('  Wallets created')

        # ── Bookings + Payments + Tickets ──
        booking_statuses = ['confirmed', 'confirmed', 'confirmed', 'completed', 'completed', 'cancelled', 'pending']
        booking_counter = 0
        user_list = list(users.values())
        active_buses = [b for b in buses if b.status == 'active' and b.route]
        if not active_buses:
            active_buses = buses[:5]

        today = timezone.now().date()
        for user in user_list:
            num_bookings = random.randint(1, 4)
            for _ in range(num_bookings):
                bus = random.choice(active_buses)
                status = random.choice(booking_statuses)
                passengers_count = random.randint(1, 3)
                price = random.randint(300, 2500)
                total = Decimal(str(price * passengers_count))
                discount = Decimal(str(random.choice([0, 0, 0, 50, 100])))
                conv_fee = Decimal(str(random.choice([0, 20, 30, 49])))
                final = total - discount + conv_fee
                journey_date = today + timedelta(days=random.randint(-30, 14))

                booking = Booking(
                    user=user, bus=bus, route=bus.route,
                    booking_id=uuid.uuid4().hex[:12].upper(),
                    journey_date=journey_date,
                    boarding_point=f'{bus.route.origin.name} Bus Stand',
                    dropping_point=f'{bus.route.destination.name} Bus Terminal',
                    total_passengers=passengers_count,
                    total_amount=total, discount_amount=discount,
                    convenience_fee=conv_fee, final_amount=final,
                    status=status,
                    booked_at=timezone.now() - timedelta(days=random.randint(0, 60)),
                )
                booking.save()
                booking_counter += 1

                # Passengers
                for p in range(passengers_count):
                    Passenger.objects.create(
                        booking=booking,
                        name=f'{user.first_name} {user.last_name}' if p == 0 else f'Passenger {p+1}',
                        age=random.randint(18, 65),
                        gender=random.choice(['M', 'F']),
                        seat_number=f'{random.randint(1,10)}{random.choice(["A","B","C","D","E"])}',
                        is_primary=(p == 0),
                    )

                # Payment
                if status != 'pending':
                    pay_status = 'success' if status in ('confirmed', 'completed') else ('refunded' if status == 'cancelled' else 'pending')
                    Payment.objects.create(
                        booking=booking, user=user,
                        amount=final,
                        method=random.choice(['upi', 'card', 'wallet', 'netbanking']),
                        status=pay_status,
                        paid_at=booking.booked_at if pay_status == 'success' else None,
                    )

                # Ticket
                if status in ('confirmed', 'completed'):
                    Ticket.objects.create(
                        booking=booking,
                        status='confirmed' if status == 'confirmed' else 'confirmed',
                    )

        self.stdout.write(f'  Bookings: {booking_counter}')

        # ── Support Tickets ──
        ticket_subjects = [
            ('Bus was late by 2 hours', 'booking', 'high'),
            ('Refund not received for cancelled booking', 'refund', 'medium'),
            ('AC not working during journey', 'bus_quality', 'medium'),
            ('Driver was driving rashly', 'driver', 'high'),
            ('Payment failed but amount deducted', 'payment', 'high'),
            ('Wrong bus boarding point shown', 'booking', 'low'),
            ('Need to reschedule my booking', 'cancellation', 'medium'),
        ]
        for user in random.sample(user_list, min(5, len(user_list))):
            subj, cat, pri = random.choice(ticket_subjects)
            SupportTicket.objects.create(
                user=user, subject=subj,
                description=f'User reported: {subj}. This needs immediate attention from the support team.',
                category=cat, priority=pri,
                status=random.choice(['open', 'open', 'in_progress', 'resolved']),
            )
        self.stdout.write('  Support Tickets created')

        # ── Emergency Alerts ──
        for user in random.sample(user_list, min(2, len(user_list))):
            EmergencyAlert.objects.create(
                user=user, title='SOS - Medical Emergency',
                description='Passenger needs immediate medical assistance on bus.',
                location=f'Near {random.choice(list(cities.keys()))} Highway',
                priority='critical',
            )
        self.stdout.write('  Emergency Alerts created')

        # ── Login Logs + Audit Logs ──
        for user in random.sample(user_list, min(5, len(user_list))):
            LoginLog.objects.create(
                user=user, username_attempted=user.username,
                ip_address=f'192.168.1.{random.randint(1,254)}',
                user_agent='Mozilla/5.0', is_success=True,
            )
        AuditLog.objects.create(
            user=User.objects.filter(is_superuser=True).first(),
            action='login', resource='admin_portal',
            details='Admin login successful', ip_address='127.0.0.1',
        )
        self.stdout.write('  Login Logs & Audit Logs created')

        # ── CMS Content ──
        Banner.objects.get_or_create(
            title='Monsoon Travel Sale - 30% Off!',
            defaults={'description': 'Book your monsoon getaway with up to 30% off on all routes.', 'sort_order': 1, 'is_active': True}
        )
        Banner.objects.get_or_create(
            title='GoBus Premium - Luxury Coaches',
            defaults={'description': 'Travel in comfort with our premium Volvo and Scania fleet.', 'sort_order': 2, 'is_active': True}
        )
        Banner.objects.get_or_create(
            title='Refer & Earn - Get ₹200',
            defaults={'description': 'Invite friends and earn ₹200 for every successful referral.', 'sort_order': 3, 'is_active': True}
        )
        BlogPost.objects.get_or_create(
            slug='top-10-travel-tips',
            defaults={'title': 'Top 10 Tips for a Comfortable Bus Journey', 'content': 'Pack light, carry snacks, wear comfortable clothes...', 'author': 'GoBus Team', 'is_published': True}
        )
        BlogPost.objects.get_or_create(
            slug='safe-travel-guide',
            defaults={'title': 'How to Travel Safely During Night', 'content': 'Always share your live location, keep emergency contacts handy...', 'author': 'GoBus Team', 'is_published': True}
        )
        FAQ.objects.get_or_create(
            question='How do I cancel my booking?',
            defaults={'answer': 'Go to My Bookings, select the booking, and click Cancel. Refund will be processed within 5-7 business days.', 'category': 'booking', 'sort_order': 1}
        )
        FAQ.objects.get_or_create(
            question='Can I change my seat after booking?',
            defaults={'answer': 'Yes, you can modify your seat up to 2 hours before departure from the My Bookings section.', 'category': 'booking', 'sort_order': 2}
        )
        FAQ.objects.get_or_create(
            question='How does the wallet cashback work?',
            defaults={'answer': 'Cashback is credited to your wallet after a successful journey. You can use it for future bookings.', 'category': 'payment', 'sort_order': 3}
        )
        PageContent.objects.get_or_create(
            slug='privacy', defaults={'title': 'Privacy Policy', 'content': '<p>GoBus respects your privacy. We collect only necessary information...</p>'}
        )
        PageContent.objects.get_or_create(
            slug='terms', defaults={'title': 'Terms of Service', 'content': '<p>By using GoBus, you agree to our terms and conditions...</p>'}
        )
        self.stdout.write('  CMS content created')

        # ── Coupons ──
        Coupon.objects.get_or_create(
            code='WELCOME50', defaults={
                'discount_type': 'percentage', 'discount_value': Decimal('50'),
                'min_amount': Decimal('200'), 'max_uses': 1000,
                'valid_from': timezone.now(), 'valid_until': timezone.now() + timedelta(days=90),
            }
        )
        Coupon.objects.get_or_create(
            code='MONSOON30', defaults={
                'discount_type': 'percentage', 'discount_value': Decimal('30'),
                'min_amount': Decimal('500'), 'max_uses': 500,
                'valid_from': timezone.now(), 'valid_until': timezone.now() + timedelta(days=60),
            }
        )
        Coupon.objects.get_or_create(
            code='FLAT200', defaults={
                'discount_type': 'flat', 'discount_value': Decimal('200'),
                'min_amount': Decimal('1000'), 'max_uses': 200,
                'valid_from': timezone.now(), 'valid_until': timezone.now() + timedelta(days=30),
            }
        )
        self.stdout.write('  Coupons created')

        # ── Festival Campaigns & Flash Sales ──
        FestivalCampaign.objects.get_or_create(
            title='Diwali Dhamaka Sale',
            defaults={
                'description': 'Celebrate Diwali with amazing travel deals. Up to 40% off on all routes!',
                'discount_percent': Decimal('40'), 'coupon_code': 'DIWALI40',
                'start_date': today - timedelta(days=10), 'end_date': today + timedelta(days=20),
            }
        )
        FestivalCampaign.objects.get_or_create(
            title='Independence Day Special',
            defaults={
                'description': 'Freedom to travel! Flat 25% off on long-distance routes.',
                'discount_percent': Decimal('25'), 'coupon_code': 'FREEDOM25',
                'start_date': today - timedelta(days=5), 'end_date': today + timedelta(days=10),
            }
        )
        FlashSale.objects.get_or_create(
            title='Flash Friday - Limited Seats!',
            defaults={
                'description': 'Grab seats at unbelievable prices. Hurry, limited time only!',
                'discount_percent': Decimal('35'), 'coupon_code': 'FLASH35',
                'start_date': timezone.now(), 'end_date': timezone.now() + timedelta(hours=24),
                'max_uses': 50,
            }
        )
        self.stdout.write('  Campaigns & Flash Sales created')

        # ── Mass Notifications ──
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            MassNotification.objects.get_or_create(
                title='Monsoon Travel Advisory',
                defaults={
                    'message': 'Heavy rains expected in Mumbai and Pune. Check your travel status before departure.',
                    'type': 'announcement', 'target_role': 'all', 'created_by': admin_user,
                }
            )
            MassNotification.objects.get_or_create(
                title='New Routes Added - Goa Express',
                defaults={
                    'message': 'We have added new premium services on Mumbai-Goa route. Book now!',
                    'type': 'email', 'target_role': 'user', 'created_by': admin_user,
                }
            )
        self.stdout.write('  Mass Notifications created')

        self.stdout.write(self.style.SUCCESS('\nDone! Database seeded with realistic GoBus data.'))
