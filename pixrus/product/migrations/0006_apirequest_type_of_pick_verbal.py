# Generated by Django 5.1.1 on 2024-12-17 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_apirequest_type_of_pick'),
    ]

    operations = [
        migrations.AddField(
            model_name='apirequest',
            name='type_of_pick_verbal',
            field=models.CharField(default='Moneyline', max_length=255),
            preserve_default=False,
        ),
    ]
