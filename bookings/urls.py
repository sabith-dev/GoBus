from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list_view, name='booking_list'),
    path('create/<int:schedule_id>/', views.booking_create_view, name='booking_create'),
    path('<uuid:booking_id>/', views.booking_detail_view, name='booking_detail'),
    path('<uuid:booking_id>/confirm/', views.booking_confirm_view, name='booking_confirm'),
]
