# Generated by Django 5.1 on 2024-08-13 21:51

import shortuuid.django_fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ayadiapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='transaction_id',
            field=shortuuid.django_fields.ShortUUIDField(alphabet=None, length=15, max_length=20, prefix='TRN', unique=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('failed', 'failed'), ('completed', 'completed'), ('pending', 'pending'), ('processing', 'processing'), ('request_sent', 'request_sent'), ('request_settled', 'request settled'), ('request_processing', 'request processing')], default='pending', max_length=100),
        ),
    ]
