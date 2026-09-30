from django import forms
from .models import Payment


class PaymentForm(forms.Form):
    METHOD_CHOICES = [
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]

    method = forms.ChoiceField(choices=METHOD_CHOICES, widget=forms.RadioSelect)
    upi_id = forms.CharField(max_length=100, required=False, label='UPI ID')
    card_number = forms.CharField(max_length=16, required=False, label='Card Number')
    card_expiry = forms.CharField(max_length=5, required=False, label='Expiry (MM/YY)')
    card_cvv = forms.CharField(max_length=4, required=False, label='CVV')
    bank = forms.CharField(max_length=100, required=False, label='Select Bank')


class RefundForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea, label='Reason for Refund')
