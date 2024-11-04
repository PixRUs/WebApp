from pixrus.DatabaseDrivers.models.UserProfile import Buyer, Seller, UserProfile
from pixrus.DatabaseDrivers.models.Products import Subscription
from django.utils import timezone

def create_new_subscription(start_time, end_time, buyer, seller, meta_data):
    """
    Creates a new subscription for a buyer and seller with a specified start and end time.
    
    :param start_time: The start time of the subscription (datetime object).
    :param end_time: The end time of the subscription (datetime object).
    :param buyer: Buyer instance (Buyer model).
    :param seller: Seller instance (Seller model).
    :param meta_data: Optional dictionary of metadata for the subscription.
    :return: The created Subscription instance.
    """
    # Check that end time is after start time
    if end_time <= start_time:
        raise ValueError("End time must be after start time.")
    
    # Create the subscription
    subscription = Subscription.objects.create(
        seller=seller,
        buyer=buyer,
        subscribed_at=start_time,
        subscribed_until=end_time,
        meta_data=meta_data
    )
    
    return subscription

from django.utils import timezone
from pixrus.DatabaseDrivers.models.Products import Subscription
from pixrus.DatabaseDrivers.models.UserProfile import Buyer, Seller

def end_current_subscription(buyer, seller):
    """
    Ends the current active subscription for the specified buyer and seller.
    
    :param buyer: Buyer instance (Buyer model).
    :param seller: Seller instance (Seller model).
    :return: True if the subscription was successfully ended, False if no active subscription was found.
    """
    # Find the active subscription for the given buyer and seller
    try:
        subscription = Subscription.objects.filter(
            buyer=buyer,
            seller=seller,
            subscribed_until__gt=timezone.now()
        ).latest('subscribed_at')  # Get the latest active subscription
        
        # End the subscription by setting `subscribed_until` to the current time
        subscription.subscribed_until = timezone.now()
        subscription.save()
        return True

    except Subscription.DoesNotExist:
        # No active subscription found
        return False
    
