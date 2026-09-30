from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ReferralCode, Referral


@login_required
def referral_view(request):
    referral_code, created = ReferralCode.objects.get_or_create(user=request.user)
    referrals = Referral.objects.filter(referrer=request.user)
    return render(request, 'referrals/referrals.html', {
        'referral_code': referral_code,
        'referrals': referrals
    })


@login_required
def apply_referral_view(request):
    if request.method == 'POST':
        code = request.POST.get('referral_code', '').strip().upper()
        try:
            referral_code = ReferralCode.objects.get(code=code, is_active=True)
            if referral_code.user != request.user:
                Referral.objects.create(
                    referrer=referral_code.user,
                    referred_user=request.user,
                    referral_code=referral_code
                )
                messages.success(request, 'Referral applied! You will receive bonus after your first booking.')
            else:
                messages.error(request, 'You cannot use your own referral code.')
        except ReferralCode.DoesNotExist:
            messages.error(request, 'Invalid referral code.')
    return redirect('referrals:referrals')
