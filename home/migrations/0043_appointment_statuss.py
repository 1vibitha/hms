# Generated by Django 5.1.7 on 2025-04-02 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0042_alter_room_room_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='statuss',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending', max_length=20),
        ),
    ]
