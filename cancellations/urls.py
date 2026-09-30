from django.urls import path
from . import views

app_name = 'cancellations'

urlpatterns = [
    path('', views.cancellation_list_view, name='cancellation_list'),
    path('create/<uuid:booking_id>/', views.cancellation_create_view, name='cancellation_create'),
    path('<uuid:cancellation_id>/', views.cancellation_detail_view, name='cancellation_detail'),
]
