import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import (UserRegistrationForm, LoginForm, OTPVerificationForm,
                    ForgotPasswordForm, ResetPasswordForm)
from .models import User, PassengerProfile, AgencyProfile

USER_TYPE_LABELS = {
    'passenger': 'Passenger',
    'agency': 'Agency',
}


def register_view(request, user_type=None):
    if request.method == 'POST':
        post_data = request.POST.copy()
        if user_type:
            post_data['user_type'] = user_type
        else:
            post_data['user_type'] = 'passenger'
        form = UserRegistrationForm(post_data)
        if form.is_valid():
            user = form.save(commit=False)
            otp = ''.join(random.choices(string.digits, k=6))
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()

            if user.user_type == 'passenger':
                PassengerProfile.objects.create(user=user)
            elif user.user_type == 'agency':
                AgencyProfile.objects.create(
                    user=user,
                    agency_name=user.username,
                    agency_code='AG' + str(user.id).zfill(5)
                )

            messages.success(request, 'Account created successfully! Please sign in.')
            if user.is_agency:
                return redirect('accounts:agency_login')
            return redirect('accounts:passenger_login')
    else:
        form = UserRegistrationForm(
            initial={'user_type': user_type} if user_type else {}
        )
    template = 'accounts/agency_register.html' if user_type == 'agency' else 'accounts/register.html'
    return render(request, template, {
        'form': form,
        'user_type': user_type,
    })


def verify_otp_view(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if user.otp == otp and timezone.now() - user.otp_created_at < timedelta(minutes=10):
                user.email_verified = True
                user.otp = None
                user.save()
                messages.success(request, 'Email verified successfully!')
                if user.is_passenger:
                    return redirect('accounts:passenger_login')
                elif user.is_agency:
                    return redirect('accounts:agency_login')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Invalid or expired OTP.')
    else:
        form = OTPVerificationForm()
    return render(request, 'accounts/verify_otp.html', {'form': form, 'user': user})


def login_view(request, user_type=None):
    if request.method == 'POST':
        post_data = request.POST.copy()
        if user_type:
            post_data['user_type'] = user_type
        form = LoginForm(request, data=post_data)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user_type and user.user_type != user_type:
                    messages.error(
                        request,
                        f'This is the {USER_TYPE_LABELS.get(user_type)} login page. '
                        f'Please use the "{user.get_user_type_display()}" login instead.'
                    )
                    return redirect('accounts:login')
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                if user.is_passenger:
                    return redirect('passengers:dashboard')
                elif user.is_agency:
                    return redirect('agencies:dashboard')
                elif user.is_admin_user:
                    return redirect('admin:index')
    else:
        form = LoginForm()
    template = 'accounts/agency_login.html' if user_type == 'agency' else 'accounts/login.html'
    return render(request, template, {'form': form, 'user_type': user_type})


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('core:home')


def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                otp = ''.join(random.choices(string.digits, k=6))
                user.otp = otp
                user.otp_created_at = timezone.now()
                user.save()
                messages.success(request, 'OTP sent to your email.')
                return redirect('accounts:reset_password', user_id=user.id)
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password.html', {'form': form})


def reset_password_view(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            otp = request.POST.get('otp')
            if user.otp == otp and timezone.now() - user.otp_created_at < timedelta(minutes=10):
                user.set_password(form.cleaned_data['new_password'])
                user.otp = None
                user.save()
                messages.success(request, 'Password reset successful!')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Invalid OTP.')
    else:
        form = ResetPasswordForm()
    return render(request, 'accounts/reset_password.html', {'form': form, 'user': user})


@login_required
def profile_view(request):
    user = request.user
    context = {'user': user}
    if user.is_passenger:
        context['profile'] = user.passenger_profile
    elif user.is_agency:
        context['profile'] = user.agency_profile
    return render(request, 'accounts/profile.html', context)
