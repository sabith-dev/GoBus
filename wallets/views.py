from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wallet, WalletTransaction


@login_required
def wallet_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all()[:20]
    return render(request, 'wallets/wallet.html', {'wallet': wallet, 'transactions': transactions})


@login_required
def add_money_view(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        if amount > 0:
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.add_money(amount)
            messages.success(request, f'₹{amount} added to wallet!')
            return redirect('wallets:wallet')
    return render(request, 'wallets/add_money.html')


@login_required
def transaction_history_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all()
    return render(request, 'wallets/transactions.html', {'transactions': transactions, 'wallet': wallet})
