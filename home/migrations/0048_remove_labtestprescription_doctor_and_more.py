# Generated by Django 5.1.7 on 2025-04-02 16:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0047_alter_labtestbooking_test_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='labtestprescription',
            name='doctor',
        ),
        migrations.RemoveField(
            model_name='labtestprescription',
            name='patient',
        ),
        migrations.DeleteModel(
            name='LabTestBooking',
        ),
        migrations.DeleteModel(
            name='LabTestPrescription',
        ),
    ]
