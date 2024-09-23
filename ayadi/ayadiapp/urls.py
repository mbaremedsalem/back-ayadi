from django.urls import path
from .views import *

urlpatterns = [
    path('transaction/create/', create_transaction, name='create_transaction'),
    # ---- creation api seddade ----- 
    path('get-wallets/', WalletListView.as_view(), name='wallet-list'),
    path('demand_payment/', demand_payment, name='wallet-list'), 
    path('confirme_payment/', save_transaction, name='confirm-peiment'), 
    # ------ masrivi -------- #
    # ---- notification ---- #
    path('notification/payment/', payment_notification, name='payment_notification'),
    #----- peiment success ----
    path('payment/success/', payment_success, name='payment_success'),
    # ------- Decline URL for declined payments
    path('payment/decline/', payment_declined, name='payment_declined'),
    # Cancel URL for canceled payments
    path('payment/cancel/', payment_canceled, name='payment_canceled'),
]
