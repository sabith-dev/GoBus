from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('passenger/login/', views.login_view, {'user_type': 'passenger'}, name='passenger_login'),
    path('passenger/register/', views.register_view, {'user_type': 'passenger'}, name='passenger_register'),
    path('agency/login/', views.login_view, {'user_type': 'agency'}, name='agency_login'),
    path('agency/register/', views.register_view, {'user_type': 'agency'}, name='agency_register'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/<int:user_id>/', views.verify_otp_view, name='verify_otp'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<int:user_id>/', views.reset_password_view, name='reset_password'),
    path('profile/', views.profile_view, name='profile'),
]
