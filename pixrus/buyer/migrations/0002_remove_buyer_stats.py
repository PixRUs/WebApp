# Generated by Django 5.1.1 on 2024-12-18 20:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buyer', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buyer',
            name='stats',
        ),
    ]
