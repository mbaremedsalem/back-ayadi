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
from rest_framework_api_key.permissions import HasAPIKey

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
            montant=montant,
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
    


@api_view(["POST"])
@permission_classes([HasAPIKey])
def save_transaction(request):
    # Récupérer les données du corps de la requête
    id_facture = request.data.get("id_facture")
    id_transaction = request.data.get("id_transaction")
    montant = request.data.get("montant")
    telephone_commercant = request.data.get("telephone_commercant")
    numero_recu = request.data.get("numero_recu")
    note = request.data.get("note")

    # Vérifier que les champs obligatoires sont présents
    if not id_facture or not montant:
        return Response({"error": "Les champs 'id_facture' et 'montant' sont obligatoires."}, status=400)
    
    # Vérifier si la facture avec le même id_facture et montant existe
    try:
        facture = Facture.objects.get(id_facture=id_facture, montant=montant)
    except Facture.DoesNotExist:
        return Response({"error": "La facture avec cet 'id_facture' et 'montant' n'existe pas."}, status=400)
    
    # Créer la transaction et l'associer à la facture
    transaction = Transaction.objects.create(id_transaction=id_transaction, facture=facture)
    
    return Response({"success": "Transaction créée avec succès.", "id_transaction": transaction.id_transaction}, status=200)

# ------ masrivi -------- 
@api_view(['POST'])
@permission_classes([AllowAny])
def payment_notification(request):
    try:
        # Example of expected fields in the request
        payment_id = request.data.get('payment_id')
        status_payment = request.data.get('status')  # e.g., 'PAID', 'FAILED', etc.

        if not payment_id or not status_payment:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Log or process the payment status as needed
        # For example, update the payment record in your database
        # You can fetch the payment from the database using payment_id and update the status

        # Example: Update payment status in your database
        # payment = get_object_or_404(Payment, id=payment_id)
        # payment.status = status_payment
        # payment.save()

        # Return a success response to acknowledge the notification
        return Response({"message": "Payment notification received"}, status=status.HTTP_200_OK)

    except Exception as e:
        # Log the error and return a server error response
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([AllowAny])
def payment_success(request):
    # Retrieve payment details from query parameters
    payment_id = request.GET.get('payment_id')
    amount = request.GET.get('amount')

    # Check if required parameters are present
    if not payment_id or not amount:
        return Response({"error": "Payment details missing"}, status=400)

    # Here you can verify the payment details if necessary
    # For example, checking against the database or external service

    # Return the success response with payment details
    return Response({
        "message": "Payment successful!",
        "payment_id": payment_id,
        "amount": amount
    }, status=200)




@api_view(['GET'])
@permission_classes([AllowAny])
def payment_declined(request):
    # Retrieve payment details from query parameters
    payment_id = request.GET.get('payment_id')
    reason = request.GET.get('reason')

    # Check if required parameters are present
    if not payment_id or not reason:
        return Response({"error": "Payment details missing"}, status=400)

    # Log or process the declined payment details here if necessary

    # Return the decline response with payment details
    return Response({
        "message": "Payment declined.",
        "payment_id": payment_id,
        "reason": reason
    }, status=200)



@api_view(['GET'])
@permission_classes([AllowAny])
def payment_canceled(request):
    # Retrieve payment details from query parameters
    payment_id = request.GET.get('payment_id')
    cancel_reason = request.GET.get('reason')

    # Check if required parameters are present
    if not payment_id:
        return Response({"error": "Payment ID is missing."}, status=400)

    # Log or process the cancellation details here if necessary

    # Return the cancel response with payment details
    return Response({
        "message": "Payment was canceled by the user.",
        "payment_id": payment_id,
        "reason": cancel_reason or "No reason provided"
    }, status=200)

