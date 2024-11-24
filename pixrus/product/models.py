
import uuid
from django.db import models
from django.utils import timezone
from buyer.models import Buyer
from seller.models import Seller

class ActivePick(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='active_pick_seller')
    posted_at = models.DateTimeField(auto_now_add=True)
    event_start = models.DateTimeField(null = True)
    pick_data = models.JSONField(null=True, blank=True)
    type_of_pick = models.CharField(max_length=50, null=True, blank=True)
    game_data = models.JSONField(null=True, blank=True)
    buyers_with_access = models.ManyToManyField(Buyer, related_name='active_picks_buyer_access', blank=True)

    def has_access(self, buyer):
        return self.buyers_with_access.filter(id=buyer.id).exists()

    def make_historical(self,pick_data,event_result):
        historical_pick = HistoricalPick.objects.create(
            seller=self.seller,
            posted_at=self.posted_at,
            game_event_result=event_result,
            type_of_pick=self.type_of_pick,
            pick_data=pick_data,
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='historical_pick_seller')
    posted_at = models.DateTimeField()
    event_time_done = models.DateTimeField(null=True)
    game_event_result = models.JSONField()
    pick_data = models.JSONField()
    type_of_pick = models.CharField(max_length=50, null=True, blank=True)
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


class ApiRequest(models.Model):
    endpoint = models.CharField(null=False,max_length=255)  # The API endpoint that was called
    request_time = models.DateTimeField(null=False,auto_now_add=True)  # Time of the API request
    response_data = models.JSONField(null=False, blank=True)  # Store the API response, if needed
    sport = models.CharField(null=False,max_length=100)
    league = models.CharField(max_length=100,blank=True,null=True)
    type_of_pick = models.CharField(null=False,max_length=50, blank=True)
    delta = models.IntegerField(null=False,default=30)  # or any default integer value

    class Meta:
        verbose_name = "Vendor API Request"
        verbose_name_plural = "Vendor API Requests"
        ordering = ['-request_time']

    @classmethod
    def is_within_delta(cls, api_request):
        # Get the current time
        current_time = timezone.now()

        # Calculate the time difference
        time_difference = current_time - api_request.request_time

        # Compare the time difference in seconds with delta (converted to seconds)
        delta_in_seconds = api_request.delta * 60  # Assuming delta is in minutes
        return time_difference.total_seconds() < delta_in_seconds

    @classmethod
    def get_request_data(cls, sport, league, type_of_pick):
        queryset = cls.objects.filter(sport=sport,league=league,type_of_pick=type_of_pick)
        if not queryset.exists():  # Check if queryset is empty
            return None

        api_request = queryset.first()
        # Check if response_data is None or empty or if it's within delta
        if (
            api_request.response_data is None or
            api_request.response_data == {} or
            cls.is_within_delta(api_request)  # Corrected call here
        ):
            return None

        return api_request.response_data


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
