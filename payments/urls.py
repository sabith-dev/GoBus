from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<uuid:booking_id>/', views.payment_process_view, name='payment_process'),
    path('history/', views.payment_history_view, name='payment_history'),
    path('<uuid:payment_id>/', views.payment_detail_view, name='payment_detail'),
]
