import uuid
from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.db.models.signals import post_save
from django.dispatch import receiver


class Wallet(models.Model):
    moyen_paiement = models.CharField(max_length=100)
    code_abonnement = models.CharField(max_length=100 ,default='70abcfa8-2fb3-4741-af99-1304d8ea876b')
    type = models.CharField(max_length=100, default="wallet")

    def __str__(self):
        return self.moyen_paiement
    
class Facture(models.Model):
    id_facture = models.CharField(max_length=20, unique=True, default='',blank=True, null=True) 
    date_paiement = models.DateTimeField(blank=True, null=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    telephone_commercant = models.CharField(max_length=20,blank=True, null=True) 
    numero_recu = models.CharField(max_length=20, unique=True,blank=True, null=True) 
    note = models.CharField(max_length=20, blank=True, null=True) 

    def __str__(self):
        return self.id_facture
    
TRANSACTION_STATUS = (
    ("Failed", "Failed"),
    ("Completed", "Completed"),
    ("Pending", "Pending"),
    ("Processing", "Processing"),
)

class Transaction(models.Model):
    id_transaction = ShortUUIDField(unique=True, length=15, max_length=20, prefix="TRN",blank=True, null=True)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE,blank=True, null=True)
    status = models.CharField(choices=TRANSACTION_STATUS, max_length=100, default="Pending")

    def __str__(self):
        return f"Transaction {self.id_transaction} - {self.status}"


# Signal to create a Transaction whenever a new Facture is created
@receiver(post_save, sender=Facture)
def create_transaction_for_facture(sender, instance, created, **kwargs):
    if created:
        Transaction.objects.create(facture=instance)