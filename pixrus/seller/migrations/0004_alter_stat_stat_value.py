# Generated by Django 5.1.1 on 2024-12-04 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seller', '0003_stat_stat_verbal_alter_stat_stat_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stat',
            name='stat_value',
            field=models.FloatField(),
        ),
    ]
