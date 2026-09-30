from django.db import models
from django.conf import settings
import uuid


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'

    def __str__(self):
        return f'Wallet: {self.user.username} - ₹{self.balance}'

    def add_money(self, amount):
        self.balance += amount
        self.save()
        WalletTransaction.objects.create(wallet=self, amount=amount, transaction_type='credit', description='Money added')

    def deduct_money(self, amount, description=''):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            WalletTransaction.objects.create(wallet=self, amount=amount, transaction_type='debit', description=description)
            return True
        return False


class WalletTransaction(models.Model):
    TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('refund', 'Refund'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.CharField(max_length=200, blank=True)
    reference_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Wallet Transaction'
        verbose_name_plural = 'Wallet Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.transaction_type} - ₹{self.amount} - {self.wallet.user.username}'
