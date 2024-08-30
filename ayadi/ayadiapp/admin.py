from django.contrib import admin
from .models import *

class FactureAdmin(admin.ModelAdmin):
    list_display = ['id_facture','date_paiement','montant', 'telephone_commercant','numero_recu']  # Assurez-vous que full_name est un champ valide dans votre modèle User
    list_editable = ['telephone_commercant'] 
    search_fields = ["date_paiement","telephone_commercant","numero_recu"]
    list_filter = ["date_paiement","telephone_commercant","numero_recu"]

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id_transaction','status']  # Assurez-vous que full_name est un champ valide dans votre modèle User
    list_editable = ['status'] 
    search_fields = ['id_transaction','status']
    list_filter = ['id_transaction','status']

admin.site.register(Wallet),
admin.site.register(Transaction,TransactionAdmin),
admin.site.register(Facture,FactureAdmin),



