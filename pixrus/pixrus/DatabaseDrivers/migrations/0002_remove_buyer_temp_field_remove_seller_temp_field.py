# Generated by Django 5.1.2 on 2024-11-03 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DatabaseDrivers', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buyer',
            name='temp_field',
        ),
        migrations.RemoveField(
            model_name='seller',
            name='temp_field',
        ),
    ]
