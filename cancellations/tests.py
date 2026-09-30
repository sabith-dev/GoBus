from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, timedelta
from cancellations.models import Cancellation, CancellationPolicy
from bookings.models import Booking
from buses.models import Bus, BusType
from routes.models import Route
from schedules.models import Schedule

User = get_user_model()


class CancellationPolicyTest(TestCase):
    def test_create_policy(self):
        policy = CancellationPolicy.objects.create(
            name='24hr Policy',
            hours_before_departure=24,
            cancellation_fee_percentage=10.00
        )
        self.assertEqual(policy.hours_before_departure, 24)
        self.assertEqual(policy.cancellation_fee_percentage, 10.00)

    def test_policy_str(self):
        policy = CancellationPolicy.objects.create(
            name='48hr Policy',
            hours_before_departure=48,
            cancellation_fee_percentage=5.00
        )
        self.assertIn('48hr', str(policy))


class CancellationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='canceller',
            password='testpass123',
            user_type='passenger'
        )
        self.agency = User.objects.create_user(
            username='cancelagency',
            password='testpass123',
            user_type='agency'
        )
        self.bus_type = BusType.objects.create(name='AC', total_seats=10)
        self.bus = Bus.objects.create(
            agency=self.agency,
            bus_type=self.bus_type,
            bus_number='DL01CANC01',
            bus_name='Test Bus',
            total_seats=10
        )
        self.route = Route.objects.create(
            agency=self.agency,
            name='Delhi-Jaipur',
            origin='Delhi',
            destination='Jaipur',
            distance_km=280,
            estimated_duration=timedelta(hours=5),
            base_fare=800
        )
        self.schedule = Schedule.objects.create(
            bus=self.bus,
            route=self.route,
            departure_time=time(6, 0),
            arrival_time=time(11, 0),
            fare=800,
            operating_days=[0, 1, 2, 3, 4, 5, 6],
            effective_from=date.today()
        )
        self.booking = Booking.objects.create(
            passenger=self.user,
            schedule=self.schedule,
            travel_date=date.today() + timedelta(days=7),
            passenger_name='Test Canceller',
            passenger_email='cancel@test.com',
            passenger_phone='+919999999998',
            total_amount=800,
            final_amount=800,
            status='confirmed'
        )

    def test_create_cancellation(self):
        cancellation = Cancellation.objects.create(
            booking=self.booking,
            cancelled_by=self.user,
            reason='Change of plans',
            cancellation_fee=80,
            refund_amount=720
        )
        self.assertEqual(cancellation.status, 'pending')
        self.assertEqual(cancellation.refund_amount, 720)

    def test_cancellation_str(self):
        cancellation = Cancellation.objects.create(
            booking=self.booking,
            cancelled_by=self.user,
            reason='Test cancel',
            cancellation_fee=0,
            refund_amount=800
        )
        self.assertIn('Cancellation', str(cancellation))

    def test_booking_status_after_cancel(self):
        self.booking.status = 'cancelled'
        self.booking.save()
        self.assertEqual(self.booking.status, 'cancelled')
