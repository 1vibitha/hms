# Generated by Django 5.1.7 on 2025-03-25 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_patient_payment_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='re_admit',
            field=models.BooleanField(default=False),
        ),
    ]
