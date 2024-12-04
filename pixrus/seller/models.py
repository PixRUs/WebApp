import uuid
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from pixrus.settings import STAT_NAMES,STAT_VERBALS,ALLOWED_TIME_UNITS_FOR_LEADERBOARD
class Seller(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='%(class)s_profile')
    meta_data = models.JSONField(null=True, blank=True)


class Stat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="stats")
    stat_name = models.CharField(max_length=255)
    stat_verbal = models.CharField(max_length=255)
    stat_value = models.DecimalField(max_digits=10, decimal_places=5)
    time_period = models.CharField(max_length=10, choices=[
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('all_time', 'All Time')
    ])



@receiver(post_save, sender=Seller)
def create_default_stats(sender, instance, created, **kwargs):
    if created:
        for stat in STAT_NAMES:
            for period in ALLOWED_TIME_UNITS_FOR_LEADERBOARD:
                Stat.objects.create(
                    seller=instance,
                    stat_name=stat,
                    stat_verbal=STAT_VERBALS[stat],
                    stat_value=0,  # Default value for stats
                    time_period=period
                )



