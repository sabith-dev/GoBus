from django.test import TestCase
from django.contrib.auth import get_user_model
from buses.models import Bus, BusType, Seat

User = get_user_model()


class BusTypeTest(TestCase):
    def test_create_bus_type(self):
        bus_type = BusType.objects.create(
            name='AC Sleeper',
            total_seats=40,
            is_sleeper=True,
            is_ac=True
        )
        self.assertEqual(bus_type.name, 'AC Sleeper')
        self.assertEqual(bus_type.total_seats, 40)

    def test_bus_type_str(self):
        bus_type = BusType.objects.create(name='Non-AC Seater', total_seats=50)
        self.assertEqual(str(bus_type), 'Non-AC Seater')


class BusTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='busagency',
            password='testpass123',
            user_type='agency'
        )
        self.bus_type = BusType.objects.create(
            name='AC Sleeper',
            total_seats=40,
            is_sleeper=True,
            is_ac=True
        )

    def test_create_bus(self):
        bus = Bus.objects.create(
            agency=self.user,
            bus_type=self.bus_type,
            bus_number='KA01AB1234',
            bus_name='Volvo AC Sleeper',
            total_seats=40
        )
        self.assertEqual(bus.bus_number, 'KA01AB1234')
        self.assertEqual(bus.agency, self.user)

    def test_bus_str(self):
        bus = Bus.objects.create(
            agency=self.user,
            bus_type=self.bus_type,
            bus_number='KA01AB1234',
            bus_name='Volvo AC Sleeper',
            total_seats=40
        )
        self.assertIn('Volvo AC Sleeper', str(bus))


class SeatTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='seatagency',
            password='testpass123',
            user_type='agency'
        )
        self.bus_type = BusType.objects.create(name='AC', total_seats=2)
        self.bus = Bus.objects.create(
            agency=self.user,
            bus_type=self.bus_type,
            bus_number='KA01CD5678',
            bus_name='Test Bus',
            total_seats=2
        )

    def test_create_seat(self):
        seat = Seat.objects.create(
            bus=self.bus,
            seat_number='1',
            seat_type='seater',
            row=1,
            column=1
        )
        self.assertEqual(seat.seat_number, '1')
        self.assertTrue(seat.is_available)

    def test_seat_str(self):
        seat = Seat.objects.create(
            bus=self.bus,
            seat_number='1',
            row=1,
            column=1
        )
        self.assertIn('KA01CD5678', str(seat))
