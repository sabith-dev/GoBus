from django.urls import path
from . import views

app_name = "admin_portal"

urlpatterns = [
    path("login/", views.admin_login_view, name="login"),
    path("logout/", views.admin_logout_view, name="logout"),
    path("dashboard/", views.admin_dashboard, name="dashboard"),
    path("users/", views.manage_users, name="users"),
    path("users/<int:pk>/", views.user_detail, name="user_detail"),
    path("agencies/", views.manage_agencies, name="agencies"),
    path("agencies/<int:pk>/", views.agency_detail, name="agency_detail"),
    path("buses/", views.manage_buses, name="buses"),
    path("cities/", views.manage_cities, name="cities"),
    path("offers/", views.manage_offers, name="offers"),
    path("payments/", views.manage_payments, name="payments"),
    path("support/", views.support_center, name="support"),
    path("notifications/", views.manage_notifications, name="notifications"),
    path("cms/", views.cms, name="cms"),
    path("reports/", views.reports, name="reports"),
    path("security/", views.security, name="security"),
]
