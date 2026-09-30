from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, PassengerProfile, AgencyProfile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=17, required=False)
    user_type = forms.ChoiceField(choices=[('passenger', 'Passenger'), ('agency', 'Agency')], widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'user_type', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered.')
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter OTP'}))


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class PassengerProfileForm(forms.ModelForm):
    class Meta:
        model = PassengerProfile
        fields = ['date_of_birth', 'gender', 'address', 'city', 'state', 'pincode', 'profile_photo', 'id_proof_type', 'id_proof_number']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


class AgencyProfileForm(forms.ModelForm):
    class Meta:
        model = AgencyProfile
        fields = ['agency_name', 'description', 'logo', 'website', 'contact_email', 'contact_phone', 'address', 'city', 'state', 'pincode', 'gst_number', 'pan_number']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']
