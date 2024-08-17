# from django.db import models
# from shortuuid.django_fields import ShortUUIDField

# class Wallet(models.Model):
#     moyen_paiement = models.CharField(max_length=100)
#     code_abonnement = models.CharField(max_length=100)
#     type = models.CharField(max_length=100, default="wallet")
#     image = models.ImageField(upload_to='wallet_images/', null=True, blank=True)

#     def __str__(self):
#         return self.moyen_paiement


# TRANSACTION_STATUS = (
#     ("Failed", "Failed"),
#     ("Completed", "Completed"),
#     ("Pending", "Pending"),
#     ("Processing", "Processing"),
#     ("Request_sent", "Request_sent"),
#     ("Request_settled", "Request settled"),
#     ("Request_processing", "Request processing"),

# )

# class Transaction(models.Model):
#     transaction_id = ShortUUIDField(unique=True, length=15, max_length=20, prefix="TRN")
#     montant = models.DecimalField(max_digits=10, decimal_places=2)
#     phone = models.CharField(max_length=15)
#     wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
#     date = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(choices=TRANSACTION_STATUS, max_length=100, default="pending")
#     code_paiement = models.CharField(max_length=20, blank=True, null=True)
#     remarque = models.TextField(blank=True, null=True)
#     def __str__(self):
#         return f"Transaction {self.transaction_id} - {self.montant} - {self.wallet.code_abonnement}"


import uuid
from django.db import models
from shortuuid.django_fields import ShortUUIDField

class Wallet(models.Model):
    moyen_paiement = models.CharField(max_length=100)
    code_abonnement = models.CharField(max_length=100 ,default='70abcfa8-2fb3-4741-af99-1304d8ea876b')
    type = models.CharField(max_length=100, default="wallet")


    def __str__(self):
        return self.moyen_paiement

TRANSACTION_STATUS = (
    ("Failed", "Failed"),
    ("Completed", "Completed"),
    ("Pending", "Pending"),
    ("Processing", "Processing"),
    ("Request_sent", "Request_sent"),
    ("Request_settled", "Request settled"),
    ("Request_processing", "Request processing"),
)

class Transaction(models.Model):
    transaction_id = ShortUUIDField(unique=True, length=15, max_length=20, prefix="TRN")
    id_facture = models.CharField(max_length=20, unique=True, default='', editable=False)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=TRANSACTION_STATUS, max_length=100, default="Pending")
    code_paiement = models.CharField(max_length=20, blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.montant} - {self.wallet.moyen_paiement}"

    def save(self, *args, **kwargs):
        if not self.id_facture:
            self.id_facture = self.generate_id_facture()
        super().save(*args, **kwargs)

    def generate_id_facture(self):
        return str(uuid.uuid4())[:8]  # Génère un UUID et prend les 8 premiers caractères
