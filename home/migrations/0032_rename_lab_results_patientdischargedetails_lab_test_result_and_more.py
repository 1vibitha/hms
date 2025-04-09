# Generated by Django 5.1.7 on 2025-03-31 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0031_patientdischargedetails_lab_results_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patientdischargedetails',
            old_name='lab_results',
            new_name='lab_test_result',
        ),
        migrations.RemoveField(
            model_name='patientdischargedetails',
            name='lab_tests',
        ),
        migrations.RemoveField(
            model_name='patientdischargedetails',
            name='total_lab_cost',
        ),
        migrations.AddField(
            model_name='patientdischargedetails',
            name='lab_test_cost',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='patientdischargedetails',
            name='lab_test_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
