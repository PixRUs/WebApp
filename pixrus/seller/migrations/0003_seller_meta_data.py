# Generated by Django 5.1.1 on 2024-11-15 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seller', '0002_rename_meta_data_seller_stats'),
    ]

    operations = [
        migrations.AddField(
            model_name='seller',
            name='meta_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]