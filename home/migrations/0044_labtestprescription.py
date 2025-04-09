# Generated by Django 5.1.7 on 2025-04-02 14:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0043_appointment_statuss'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabTestPrescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prescribed_tests', models.TextField()),
                ('prescribed_at', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='home.appointment')),
            ],
        ),
    ]
