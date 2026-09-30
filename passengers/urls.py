from django.urls import path
from . import views

app_name = 'passengers'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('search/', views.search_view, name='search'),
    path('results/', views.bus_results_view, name='bus_results'),
    path('bus/<int:bus_id>/', views.bus_details_view, name='bus_details'),
    path('schedule/<int:schedule_id>/seats/', views.seat_selection_view, name='seat_selection'),
    path('booking/<int:booking_id>/details/', views.passenger_details_view, name='passenger_details'),
    path('booking/<int:booking_id>/payment/', views.payment_view, name='payment'),
    path('booking/<int:booking_id>/confirmation/', views.booking_confirmation_view, name='booking_confirmation'),
    path('booking/<int:booking_id>/ticket/', views.ticket_view, name='ticket'),
    path('bookings/', views.my_bookings_view, name='my_bookings'),
    path('bookings/<int:booking_id>/', views.booking_details_view, name='booking_details'),
    path('cancellations/', views.cancellations_view, name='cancellations'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('referrals/', views.referrals_view, name='referrals'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('tracking/<int:booking_id>/', views.live_tracking_view, name='live_tracking'),
]
