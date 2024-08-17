from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import requests
from .models import *
from .serializers import *
from django.http import JsonResponse
from rest_framework.views import APIView
import uuid
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import random
import string

def send_payment_request(transaction):
    # Déterminer l'URL de l'API de la banque en fonction du wallet
    if transaction.wallet.name == 'Seddad':
        api_url = 'http://localhost/sedad.php'
    elif transaction.wallet.name == 'Bankily':
        api_url = 'https://api.bankily.com/payment'
    else:
        transaction.status = "Failed"
        transaction.save()
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer [Votre_Token]"  # Remplacer par le token réel si nécessaire
    }
    data = {
        "montant": str(transaction.montant),
        "numero_donneur": transaction.numero_donneur,
        "code_commercant": transaction.wallet.code_commercant
    }
    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 200:
        transaction.status = "Success"
    else:
        transaction.status = "Failed"
    transaction.save()

@api_view(['POST'])
@permission_classes([AllowAny])
def create_transaction(request):
    serializer = TransactionSerializer(data=request.data)
    
    if serializer.is_valid():
        # Extraire les données validées
        transaction_data = serializer.validated_data
        wallet_id = transaction_data['wallet'].id  # Assurez-vous d'utiliser l'ID du wallet
        montant = transaction_data['montant']
        numero_donneur = transaction_data['numero_donneur']
        
        try:
            # Trouver le wallet et obtenir le code commerçant
            wallet = Wallet.objects.get(id=wallet_id)
            transaction = Transaction(wallet=wallet, montant=montant, numero_donneur=numero_donneur, status="Pending")
            transaction.save()
            
            # Envoyer la requête de paiement
            send_payment_request(transaction)
            
            # Répondre en fonction du statut de la transaction
            if transaction.status == "Success":
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Wallet.DoesNotExist:
            return Response({"message": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
        except requests.RequestException as e:
            return Response({"message": f"Request failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- get moyen payement -------------------
# views.py
class WalletListView(APIView):

    def get(self, request):
        url = "https://gimtel-pay-a99c057b5927.herokuapp.com/api/moyens_paiement"
        headers = {
            "accept": "application/json",
            "Authorization": "Api-Key UaPHMqPD.WsNY4ZQkDTH2OWVuWGUHCi3W61gfwEML",
            "content-type": "application/json"
        }

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json().get('data', [])
            
            for item in data:
                # Ajouter une image à chaque wallet
                item['image'] = f"{request.build_absolute_uri('/media/wallet_images/sedad_logo_bmi.jpg')}"
                # Vous pouvez personnaliser l'image pour chaque wallet ici.

            return JsonResponse({
                "status": 200,
                "Message": "OK",
                "data": data
            }, status=200)

        return JsonResponse({"status": response.status_code, "Message": "Failed"}, status=response.status_code)


# ------- demande payment seddad --------
