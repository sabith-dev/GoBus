from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('passenger', 'Passenger'),
        ('agency', 'Agency'),
        ('admin', 'Admin'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='passenger')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Phone number must be in format: +919999999999')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.username} ({self.get_user_type_display()})'

    @property
    def is_passenger(self):
        return self.user_type == 'passenger'

    @property
    def is_agency(self):
        return self.user_type == 'agency'

    @property
    def is_admin_user(self):
        return self.user_type == 'admin'


class PassengerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='passenger_profile')
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    profile_photo = models.ImageField(upload_to='user_profiles/', blank=True, null=True)
    id_proof_type = models.CharField(max_length=20, choices=[
        ('aadhaar', 'Aadhaar Card'),
        ('pan', 'PAN Card'),
        ('passport', 'Passport'),
    ], blank=True)
    id_proof_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Passenger Profile'
        verbose_name_plural = 'Passenger Profiles'

    def __str__(self):
        return f'Passenger Profile: {self.user.username}'


class AgencyProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agency_profile')
    agency_name = models.CharField(max_length=200)
    agency_code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='agency_logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=17, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    gst_number = models.CharField(max_length=15, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_verified = models.BooleanField(default=False)
    total_buses = models.PositiveIntegerField(default=0)
    total_routes = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Agency Profile'
        verbose_name_plural = 'Agency Profiles'

    def __str__(self):
        return f'{self.agency_name} ({self.agency_code})'
