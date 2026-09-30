from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import PassengerProfile, AgencyProfile

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.passenger = User.objects.create_user(
            username='testpassenger',
            email='passenger@test.com',
            password='testpass123',
            user_type='passenger'
        )
        self.agency = User.objects.create_user(
            username='testagency',
            email='agency@test.com',
            password='testpass123',
            user_type='agency'
        )

    def test_user_creation(self):
        self.assertEqual(self.passenger.user_type, 'passenger')
        self.assertEqual(self.agency.user_type, 'agency')

    def test_user_str(self):
        self.assertIn('testpassenger', str(self.passenger))

    def test_is_passenger(self):
        self.assertTrue(self.passenger.is_passenger)
        self.assertFalse(self.agency.is_passenger)

    def test_is_agency(self):
        self.assertTrue(self.agency.is_agency)
        self.assertFalse(self.passenger.is_agency)


class RegistrationTest(TestCase):
    def test_register_passenger(self):
        response = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'phone_number': '+919999999999',
            'user_type': 'passenger',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_agency(self):
        response = self.client.post('/register/', {
            'username': 'newagency',
            'email': 'agency@test.com',
            'phone_number': '+919999999998',
            'user_type': 'agency',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newagency')
        self.assertEqual(user.user_type, 'agency')


class LoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='logintest',
            email='login@test.com',
            password='testpass123'
        )

    def test_login_success(self):
        response = self.client.post('/login/', {
            'username': 'logintest',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_failure(self):
        response = self.client.post('/login/', {
            'username': 'logintest',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
