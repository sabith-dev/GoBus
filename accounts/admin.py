from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PassengerProfile, AgencyProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'user_type', 'phone_number', 'email_verified', 'is_active', 'created_at']
    list_filter = ['user_type', 'email_verified', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'phone_number']
    ordering = ['-created_at']

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'email_verified', 'otp', 'otp_created_at')}),
    )


@admin.register(PassengerProfile)
class PassengerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'city', 'state', 'created_at']
    search_fields = ['user__username', 'user__email', 'city']
    list_filter = ['gender', 'state']


@admin.register(AgencyProfile)
class AgencyProfileAdmin(admin.ModelAdmin):
    list_display = ['agency_name', 'agency_code', 'user', 'status', 'is_verified', 'total_buses', 'rating']
    search_fields = ['agency_name', 'agency_code', 'user__username']
    list_filter = ['status', 'is_verified']
