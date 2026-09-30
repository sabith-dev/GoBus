from django.urls import path
from . import views

app_name = 'agencies'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('buses/', views.bus_list_view, name='bus_list'),
    path('buses/add/', views.bus_add_view, name='bus_add'),
    path('buses/<int:bus_id>/edit/', views.bus_edit_view, name='bus_edit'),
    path('buses/<int:bus_id>/', views.bus_details_view, name='bus_details'),
    path('buses/<int:bus_id>/seats/', views.bus_seats_view, name='bus_seats'),
    path('routes/', views.route_list_view, name='route_list'),
    path('routes/add/', views.route_add_view, name='route_add'),
    path('routes/<int:route_id>/edit/', views.route_edit_view, name='route_edit'),
    path('schedules/', views.schedule_list_view, name='schedule_list'),
    path('schedules/add/', views.schedule_add_view, name='schedule_add'),
    path('schedules/<int:schedule_id>/edit/', views.schedule_edit_view, name='schedule_edit'),
    path('passengers/', views.passenger_list_view, name='passenger_list'),
    path('passengers/<int:passenger_id>/', views.passenger_details_view, name='passenger_details'),
    path('bookings/', views.booking_list_view, name='booking_list'),
    path('bookings/<int:booking_id>/', views.booking_details_view, name='booking_details'),
    path('cancellations/', views.cancellation_list_view, name='cancellation_list'),
    path('earnings/', views.earnings_view, name='earnings'),
    path('reviews/', views.review_list_view, name='review_list'),
]
