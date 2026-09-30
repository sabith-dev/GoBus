from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    path('map/<int:booking_id>/', views.tracking_map_view, name='tracking_map'),
    path('api/location/<int:bus_id>/', views.get_bus_location_api, name='get_location'),
]
