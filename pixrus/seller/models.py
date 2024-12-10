import uuid
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import  Literal
from enum import Enum

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
    stat_value = models.FloatField()
    time_period = models.CharField(max_length=10, choices=[
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('all_time', 'All Time')
    ])

from enum import Enum
from django.db.models.signals import post_save
from django.dispatch import receiver


# Enum for Stat Names
class StatName(Enum):
    TOTAL_UNITS_WON = "total_units_won"
    NUMBER_OF_SUCCESSES = "number_of_successes"
    NUMBER_OF_FAILED_PICKS = "number_of_failed_picks"
    TOTAL_PICKS_PLACED = "total_picks_placed"
    TOTAL_PROBABILITY = "total_probability"

    # A method to return the verbal description for each stat
    @property
    def stat_verbal(self):
        return {
            StatName.TOTAL_UNITS_WON: "Units Won",
            StatName.NUMBER_OF_SUCCESSES: "Successful Bets",
            StatName.NUMBER_OF_FAILED_PICKS: "Unsuccessful Bets",
            StatName.TOTAL_PICKS_PLACED: "Total Picks Placed",
            StatName.TOTAL_PROBABILITY: "Average Risk Taken",
        }[self]

# Enum for Stat Time Units
class StatTimeUnits(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    ALL_TIME = "all_time"


# Signal handler for post_save of Seller
@receiver(post_save, sender=Seller)
def create_default_stats(sender, instance, created, **kwargs):
    if created:
        for stat in StatName:
            for period in StatTimeUnits:
                Stat.objects.get_or_create(
                    seller=instance,
                    stat_name=stat,
                    time_period=period,
                    defaults={
                        "seller": instance,
                        "stat_name": stat.value,  # Store the value of Enum
                        "stat_verbal": stat.stat_verbal,  # Access verbal description via property
                        "stat_value": 0,  # Default value for stats
                        "time_period": period.value  # Store the value of time period
                    }
                )
