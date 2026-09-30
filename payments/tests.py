from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from payments.models import Payment, Refund
from bookings.models import Booking
from buses.models import Bus, BusType
from routes.models import Route
from schedules.models import Schedule
from datetime import time

User = get_user_model()


class PaymentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='payer1',
            password='testpass123',
            user_type='passenger'
        )
        self.agency = User.objects.create_user(
            username='payagency',
            password='testpass123',
            user_type='agency'
        )
        self.bus_type = BusType.objects.create(name='AC', total_seats=10)
        self.bus = Bus.objects.create(
            agency=self.agency,
            bus_type=self.bus_type,
            bus_number='MH01PAY01',
            bus_name='Test Bus',
            total_seats=10
        )
        self.route = Route.objects.create(
            agency=self.agency,
            name='Mumbai-Pune',
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
        self.booking = Booking.objects.create(
            passenger=self.user,
            schedule=self.schedule,
            travel_date=date.today() + timedelta(days=1),
            passenger_name='Test Payer',
            passenger_email='payer@test.com',
            passenger_phone='+919999999999',
            total_amount=500,
            final_amount=500,
            status='confirmed'
        )

    def test_create_payment(self):
        payment = Payment.objects.create(
            booking=self.booking,
            user=self.user,
            amount=500,
            method='upi',
            status='completed',
            paid_at=timezone.now(),
            transaction_id='TXN123456'
        )
        self.assertEqual(payment.status, 'completed')
        self.assertEqual(payment.method, 'upi')

    def test_payment_str(self):
        payment = Payment.objects.create(
            booking=self.booking,
            user=self.user,
            amount=500,
            method='card',
            status='completed'
        )
        self.assertIn('500', str(payment))

    def test_refund(self):
        payment = Payment.objects.create(
            booking=self.booking,
            user=self.user,
            amount=500,
            method='upi',
            status='completed',
            transaction_id='TXN789'
        )
        refund = Refund.objects.create(
            payment=payment,
            amount=250,
            reason='Cancelled by user',
            status='pending'
        )
        self.assertEqual(refund.amount, 250)
        self.assertEqual(refund.status, 'pending')
