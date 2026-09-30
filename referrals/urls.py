from django.urls import path
from . import views

app_name = 'referrals'

urlpatterns = [
    path('', views.referral_view, name='referrals'),
    path('apply/', views.apply_referral_view, name='apply_referral'),
]
