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
from django.utils import timezone
from django.shortcuts import get_object_or_404

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
def generate_id_facture():
    return str(uuid.uuid4())[:8]  # Génère un UUID et prend les 8 premiers caractères

id_facture = generate_id_facture()

@api_view(["POST"])
@permission_classes([AllowAny])
def demand_payment(request):
    nom_payeur = request.data.get("nom_payeur")
    prenom_payeur = request.data.get("prenom_payeur")
    montant = request.data.get("montant")
    
    if not all([nom_payeur, prenom_payeur, montant]):
        return Response({"error": "Nom, prénom et montant sont requis."}, status=400)
    
    wallet = get_object_or_404(Wallet, type="wallet")
    code_abonnement = wallet.code_abonnement
    
    current_date = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"
    print(current_date)

    data = {
        "id_facture": id_facture,
        "montant": montant,
        "nom_payeur": nom_payeur,
        "prenom_payeur": prenom_payeur,
        "date": "2024-08-15T16:52:47.720Z", 
        "code_abonnement": code_abonnement,
        "remarque": ""
    }
    
    url = "https://gimtel-pay-a99c057b5927.herokuapp.com/api/demande_paiement"
    
    headers = {
        "accept": "application/json",
        "Authorization": "Api-Key UaPHMqPD.WsNY4ZQkDTH2OWVuWGUHCi3W61gfwEML",
        "content-type": "application/json"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        # Extraire le contenu de la réponse de l'API externe
        response_data = response.json()
        
        # Retourner le contenu de la réponse de l'API externe à l'utilisateur
        return Response(response_data, status=response.status_code)
    
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=400)