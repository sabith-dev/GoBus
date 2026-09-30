from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, timedelta
from bookings.models import Booking, BookingSeat, SeatLock
from buses.models import Bus, BusType, Seat
from schedules.models import Schedule
from routes.models import Route

User = get_user_model()


class BookingTest(TestCase):
    def setUp(self):
        self.passenger = User.objects.create_user(
            username='passenger1',
            password='testpass123',
            user_type='passenger'
        )
        self.agency = User.objects.create_user(
            username='agency1',
            password='testpass123',
            user_type='agency'
        )
        self.bus_type = BusType.objects.create(name='AC', total_seats=2)
        self.bus = Bus.objects.create(
            agency=self.agency,
            bus_type=self.bus_type,
            bus_number='KA01XY9999',
            bus_name='Test Bus',
            total_seats=2
        )
        self.seat = Seat.objects.create(
            bus=self.bus,
            seat_number='1',
            row=1,
            column=1
        )
        self.route = Route.objects.create(
            agency=self.agency,
            name='Test Route',
            origin='Mumbai',
            destination='Pune',
            distance_km=150,
            estimated_duration=timedelta(hours=3),
            base_fare=500
        )
        self.schedule = Schedule.objects.create(
            bus=self.bus,
            route=self.route,
            departure_time=time(8, 0),
            arrival_time=time(11, 0),
            fare=500,
            operating_days=[0, 1, 2, 3, 4],
            effective_from=date.today()
        )

    def test_create_booking(self):
        booking = Booking.objects.create(
            passenger=self.passenger,
            schedule=self.schedule,
            travel_date=date.today() + timedelta(days=1),
            passenger_name='Test Passenger',
            passenger_email='test@test.com',
            passenger_phone='+919999999999',
            total_amount=500,
            final_amount=500
        )
        self.assertEqual(booking.status, 'pending')
        self.assertIsNotNone(booking.booking_id)

    def test_booking_seat(self):
        booking = Booking.objects.create(
            passenger=self.passenger,
            schedule=self.schedule,
            travel_date=date.today() + timedelta(days=1),
            passenger_name='Test Passenger',
            passenger_email='test@test.com',
            passenger_phone='+919999999999',
            total_amount=500,
            final_amount=500
        )
        booking_seat = BookingSeat.objects.create(
            booking=booking,
            seat=self.seat,
            passenger_name='Test Passenger',
            price=500
        )
        self.assertEqual(booking_seat.booking, booking)

    def test_seat_lock(self):
        lock = SeatLock.objects.create(
            seat=self.seat,
            user=self.passenger,
            schedule=self.schedule,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        self.assertTrue(lock.is_active)
