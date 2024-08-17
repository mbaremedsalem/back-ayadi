# Generated by Django 5.1 on 2024-08-16 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ayadiapp', '0004_rename_numero_donneur_transaction_phone_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wallet',
            name='image',
        ),
        migrations.AddField(
            model_name='transaction',
            name='code_paiement',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='id_facture',
            field=models.CharField(default='', editable=False, max_length=20, unique=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='remarque',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('Failed', 'Failed'), ('Completed', 'Completed'), ('Pending', 'Pending'), ('Processing', 'Processing'), ('Request_sent', 'Request_sent'), ('Request_settled', 'Request settled'), ('Request_processing', 'Request processing')], default='Pending', max_length=100),
        ),
    ]
