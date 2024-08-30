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
import logging

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


def generate_id_facture():
    return str(uuid.uuid4())[:8]  # Génère un UUID et prend les 8 premiers caractères

@api_view(["POST"])
@permission_classes([AllowAny])
def demand_payment(request):
    nom_payeur = request.data.get("nom_payeur")
    prenom_payeur = request.data.get("prenom_payeur")
    montant = request.data.get("montant")
    telephone_payeur = request.data.get("telephone_payeur")

    if not all([nom_payeur, prenom_payeur, montant]):
        return Response({"error": "Nom, prénom et montant sont requis."}, status=400)
    
    # Générer un nouvel id_facture pour chaque requête
    id_facture = generate_id_facture()
    
    wallet = get_object_or_404(Wallet, type="wallet")
    code_abonnement = wallet.code_abonnement
    
    current_date = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + "Z"
    print(current_date)

    data = {
        "id_facture": id_facture,
        "montant": montant,
        "nom_payeur": nom_payeur,
        "prenom_payeur": prenom_payeur,
        "telephone_payeur": telephone_payeur,
        "date": current_date, 
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
        print('Response Data:', response_data)  # Debugging output
        
        # Accéder à 'code_paiement' dans la réponse
        data = response_data.get('data', {})
        numero_recu = data.get('code_paiement')
    
        # Créer et sauvegarder la facture
        facture = Facture(
            id_facture=id_facture,
            date_paiement=timezone.now(),
            montant=montant,
            telephone_commercant=telephone_payeur,
            numero_recu=numero_recu,
            note="Paiement réussi"
        )
        facture.save()
        
        # Retourner le contenu de la réponse de l'API externe à l'utilisateur
        return Response(response_data, status=response.status_code)
    
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=400)


# ------------------ confirme payment ---------------

logger = logging.getLogger(__name__)
@api_view(["POST"])
@permission_classes([AllowAny])
def confirm_payment(request):
    id_facture = request.data.get("id_facture")
    id_transaction = request.data.get("id_transaction")
    date_paiement = request.data.get("date_paiement")
    montant = request.data.get("montant")
    telephone_commercant = request.data.get("telephone_commercant")
    numero_recu = request.data.get("numero_recu")
    note = request.data.get("note")

    # Logging the incoming data
    logger.debug(f"Received data: {request.data}")

    if not all([id_facture, id_transaction, date_paiement, montant, telephone_commercant, numero_recu]):
        return Response({"error": "Tous les champs sont requis."}, status=400)

    try:
        factures = Facture.objects.all()
        for facture in factures:
            print(f"Facture: {facture.id_facture}, Date: {facture.date_paiement}, Montant: {facture.montant}, Téléphone: {facture.telephone_commercant}, Reçu: {facture.numero_recu}")


        facture = Facture.objects.get(
            id_facture=id_facture,
            date_paiement=date_paiement,
            montant=montant,
            telephone_commercant=telephone_commercant,
            numero_recu=numero_recu
        )
        logger.debug(f"Facture trouvée: {facture}")
    except Facture.DoesNotExist:
        factures = Facture.objects.all()
        for facture in factures:
            print(f"Facture: {facture.id_facture}, Date: {facture.date_paiement}, Montant: {facture.montant}, Téléphone: {facture.telephone_commercant}, Reçu: {facture.numero_recu}")

        logger.warning(f"Facture non trouvée pour les données fournies: {request.data}")
        return Response({"error": "Les données fournies ne correspondent à aucune facture existante."}, status=400)

    try:
        transaction = Transaction.objects.get(id_transaction=id_transaction, facture=facture)
        logger.debug(f"Transaction trouvée: {transaction}")
    except Transaction.DoesNotExist:
        logger.warning(f"Transaction non trouvée pour la facture {id_facture} et l'ID de transaction {id_transaction}")
        return Response({"error": "La transaction ne correspond à aucune transaction existante pour cette facture."}, status=400)

    data = {
        "id_facture": id_facture,
        "id_transaction": id_transaction,
        "date_paiement": date_paiement,
        "montant": montant,
        "telephone_commercant": telephone_commercant,
        "numero_recu": numero_recu,
        "note": note or ""
    }

    url = "https://gimtel-pay-a99c057b5927.herokuapp.com/api/confirmation_paiement"
    headers = {
        "accept": "application/json",
        "Authorization": "Api-Key UaPHMqPD.WsNY4ZQkDTH2OWVuWGUHCi3W61gfwEML",
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        logger.debug(f"Response from external API: {response_data}")
        return Response(response_data, status=response.status_code)

    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending data to external API: {e}")
        return Response({"error": str(e)}, status=400)
