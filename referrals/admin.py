from django.contrib import admin
from .models import ReferralCode, Referral


@admin.register(ReferralCode)
class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'bonus_amount', 'total_referrals', 'is_active']
    list_filter = ['is_active']


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referred_user', 'status', 'bonus_credited', 'created_at']
    list_filter = ['status', 'bonus_credited']
