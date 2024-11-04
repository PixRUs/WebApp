import uuid
from django.db import models
from django.utils import timezone
from .UserProfile import Seller, Buyer

class Pick(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_id = models.CharField(max_length=255, unique=True)
    api_vendor_id = models.CharField(max_length=255)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='picks')
    posted_at = models.DateTimeField(auto_now_add=True)
    has_happened = models.BooleanField(default=False)
    meta_data = models.JSONField(null=True, blank=True)
    buyers_with_access = models.ManyToManyField(Buyer, related_name='accessible_picks', blank=True)

    def has_access(self, buyer):
        return self.buyers_with_access.filter(id=buyer.id).exists() 

class EventResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pick = models.OneToOneField(Pick, on_delete=models.CASCADE, related_name='event_result')
    result_data = models.JSONField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='subscriptions')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='subscriptions')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    subscribed_until = models.DateTimeField()
    meta_data = models.JSONField(null=True, blank=True)

    def is_active(self):
        return self.subscribed_until > timezone.now()



