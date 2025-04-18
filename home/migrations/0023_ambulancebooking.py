# Generated by Django 5.1.7 on 2025-03-30 17:34

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0022_remove_emergencyalert_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AmbulanceBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_location', models.CharField(max_length=255)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('request_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('Requested', 'Requested'), ('On the Way', 'On the Way'), ('Arrived', 'Arrived'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Requested', max_length=20)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.patient')),
            ],
        ),
    ]
