# Generated by Django 5.1 on 2024-08-17 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ayadiapp', '0007_alter_wallet_code_abonnement'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wallet',
            name='phone',
        ),
    ]
