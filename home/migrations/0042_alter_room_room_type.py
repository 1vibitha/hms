# Generated by Django 5.1.7 on 2025-04-02 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0041_alter_labtestbooking_booking_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_type',
            field=models.CharField(choices=[('General', 'General'), ('Private', 'Private')], max_length=50),
        ),
    ]
