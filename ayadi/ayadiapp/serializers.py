# serializers.py
from rest_framework import serializers
from .models import Wallet, Transaction

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['moyen_paiement', 'phone','code_abonnement', 'type']

        extra_kwargs = {
            'moyen_paiement': {'required': False, 'allow_null': True},
            'phone': {'required': False, 'allow_null': True},
            'type': {'required': False, 'allow_null': True},
            'code_abonnement': {'required': True},
        }

class TransactionSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer()

    class Meta:
        model = Transaction
        fields = ['transaction_id', 'montant', 'phone', 'wallet', 'date', 'status']

