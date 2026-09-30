from django.urls import path
from . import views

app_name = 'wallets'

urlpatterns = [
    path('', views.wallet_view, name='wallet'),
    path('add-money/', views.add_money_view, name='add_money'),
    path('transactions/', views.transaction_history_view, name='transactions'),
]
