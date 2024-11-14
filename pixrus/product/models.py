
import uuid
from django.db import models
from django.utils import timezone
from buyer.models import Buyer
from seller.models import Seller

class ActivePick(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='active_pick_seller')
    posted_at = models.DateTimeField(auto_now_add=True)
    event_start = models.DateTimeField(auto_now_add=True)
    event_data = models.JSONField(null=True, blank=True)
    buyers_with_access = models.ManyToManyField(Buyer, related_name='active_picks_buyer_access', blank=True)

    def has_access(self, buyer):
        return self.buyers_with_access.filter(id=buyer.id).exists()

    def make_historical(self, event_result):
        historical_pick = HistoricalPick.objects.create(
            id=self.id,
            seller=self.seller,
            posted_at=self.posted_at,
            event_result=event_result,
        )
        historical_pick.buyers_with_access.set(self.buyers_with_access.all())
        self.delete()
        return historical_pick

    def give_buyer_access(self, buyer):
        if not self.buyers_with_access.filter(id=buyer.id).exists():
            self.buyers_with_access.add(buyer)
        return True

    @classmethod
    def get_active_picks_for_buyer(cls, buyer):
        """
        Retrieves all active picks accessible by a specific buyer.
        """
        return cls.objects.filter(buyers_with_access=buyer)

    @classmethod
    def get_active_picks_for_seller(cls, seller):
        """
        Retrieves all active picks posted by a specific seller.
        """
        return cls.objects.filter(seller=seller)


class HistoricalPick(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='historical_pick_seller')
    posted_at = models.DateTimeField()
    meta_data = models.JSONField(null=True, blank=True)
    event_time_done = models.DateTimeField(auto_now_add=True)
    event_result = models.JSONField(null=True)
    buyers_with_access = models.ManyToManyField(Buyer, related_name='historical_pick_buyer', blank=True)

    def has_access(self, buyer):
        return self.buyers_with_access.filter(id=buyer.id).exists()

    @classmethod
    def get_historical_picks_for_buyer(cls, buyer):
        """
        Retrieves all historical picks that were accessible by a specific buyer.
        """
        return cls.objects.filter(buyers_with_access=buyer)

    @classmethod
    def get_historical_picks_for_seller(cls, seller):
        """
        Retrieves all historical picks posted by a specific seller.
        """
        return cls.objects.filter(seller=seller)


class VendorApiRequest(models.Model):
    vendor = models.CharField(max_length=255, unique=True)
    endpoint = models.CharField(max_length=255)  # The API endpoint that was called
    request_time = models.DateTimeField(auto_now_add=True)  # Time of the API request
    response_status = models.IntegerField()  # HTTP status code of the API response
    response_data = models.JSONField(null=True, blank=True)  # Store the API response, if needed
    delta = models.IntegerField(default=30)  # or any default integer value

    class Meta:
        verbose_name = "Vendor API Request"
        verbose_name_plural = "Vendor API Requests"
        ordering = ['-request_time']


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='subscriptions')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='subscriptions')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    subscribed_until = models.DateTimeField()
    meta_data = models.JSONField(null=True, blank=True)

    @classmethod
    def create_new_subscription(cls, start_time, end_time, buyer, seller, meta_data=None):
        """
        Creates a new subscription for a buyer and seller with a specified start and end time.

        :param start_time: The start time of the subscription (datetime object).
        :param end_time: The end time of the subscription (datetime object).
        :param buyer: Buyer instance (Buyer model).
        :param seller: Seller instance (Seller model).
        :param meta_data: Optional dictionary of metadata for the subscription.
        :return: The created Subscription instance.
        """
        if end_time <= start_time:
            raise ValueError("End time must be after start time.")

        # Create and return the subscription
        return cls.objects.create(
            seller=seller,
            buyer=buyer,
            subscribed_until=end_time,
            meta_data=meta_data
        )

    @classmethod
    def end_current_subscription(cls, buyer, seller):
        """
        Ends the current active subscription for the specified buyer and seller.

        :param buyer: Buyer instance (Buyer model).
        :param seller: Seller instance (Seller model).
        :return: True if the subscription was successfully ended, False if no active subscription was found.
        """
        try:
            # Find the latest active subscription where subscribed_until is in the future
            subscription = cls.objects.filter(
                buyer=buyer,
                seller=seller,
                subscribed_until__gt=timezone.now()
            ).latest('subscribed_at')

            # Delete the active subscription if found
            subscription.delete()
            return True

        except cls.DoesNotExist:
            # No active subscription found
            return False

    def is_active(self):
        return self.subscribed_until > timezone.now()
