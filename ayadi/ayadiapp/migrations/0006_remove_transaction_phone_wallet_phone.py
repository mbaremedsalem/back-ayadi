# Generated by Django 5.1 on 2024-08-17 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ayadiapp', '0005_remove_wallet_image_transaction_code_paiement_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='phone',
        ),
        migrations.AddField(
            model_name='wallet',
            name='phone',
            field=models.CharField(default='', max_length=15),
            preserve_default=False,
        ),
    ]
