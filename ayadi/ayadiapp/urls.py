from django.urls import path
from .views import *

urlpatterns = [
    path('transaction/create/', create_transaction, name='create_transaction'),
    # ---- creation api seddade ----- 
    path('get-wallets/', WalletListView.as_view(), name='wallet-list'),
    path('demand_payment/', demand_payment, name='wallet-list'), 
    path('confirme_payment/', confirm_payment, name='wallet-list'), 


]
