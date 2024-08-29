from django.urls import path
from .views import *

urlpatterns = [
    path('get-wallets/', WalletListView.as_view(), name='wallet-list'),
    path('demand_payment/', demand_payment, name='wallet-list'), 
    path('transaction/create/', create_transaction, name='create_transaction'),
]
