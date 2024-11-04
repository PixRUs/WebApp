# Generated by Django 5.1.2 on 2024-11-04 01:52

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Buyer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('meta_data', models.JSONField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pick',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('api_id', models.CharField(max_length=255, unique=True)),
                ('api_vendor_id', models.CharField(max_length=255)),
                ('posted_at', models.DateTimeField(auto_now_add=True)),
                ('has_happened', models.BooleanField(default=False)),
                ('meta_data', models.JSONField(blank=True, null=True)),
                ('buyers_with_access', models.ManyToManyField(blank=True, related_name='accessible_picks', to='DatabaseDrivers.buyer')),
            ],
        ),
        migrations.CreateModel(
            name='EventResult',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('result_data', models.JSONField(blank=True, null=True)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
                ('pick', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='event_result', to='DatabaseDrivers.pick')),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('meta_data', models.JSONField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='pick',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='picks', to='DatabaseDrivers.seller'),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('subscribed_at', models.DateTimeField(auto_now_add=True)),
                ('subscribed_until', models.DateTimeField()),
                ('meta_data', models.JSONField(blank=True, null=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='DatabaseDrivers.buyer')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='DatabaseDrivers.seller')),
            ],
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_logged_in', models.DateTimeField(blank=True, null=True)),
                ('is_online', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='session', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]