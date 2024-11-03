from .models import Pick,Buyer,Seller

from django.utils import timezone

def add_pick(api_id, api_vendor_id, seller, meta_data, event_time):
    """
    Creates and saves a new Pick instance to the database.
    """
    # Ensure event_time is timezone-aware
    if timezone.is_naive(event_time):
        event_time = timezone.make_aware(event_time)

    pick = Pick.objects.create(
        api_id=api_id,
        event_time=event_time,
        api_vendor_id=api_vendor_id,
        seller=seller,
        meta_data=meta_data
    )
    return pick


def give_buyer_access_to_pick(buyer, pick):
    """
    Grants access to a buyer for a specific pick.
    """
    try:
        # Ensure the pick instance exists
        pick = Pick.objects.get(id=pick.id)
        
        # Only add if buyer does not already have access
        if not pick.buyers_with_access.filter(id=buyer.id).exists():
            pick.buyers_with_access.add(buyer)  # Add the buyer instance itself
        
        return True

    except Pick.DoesNotExist:
        return False

    
def _get_picks(user, user_type, has_happened):
    """
    Retrieves picks based on has_happened status for a given user (buyer or seller).
    """
    try:
        if user_type == 'buyer':
            user = Buyer.objects.get(user=user)
            picks = user.accessible_picks.filter(has_happened=has_happened)
        elif user_type == 'seller':
            user = Seller.objects.get(user=user)
            picks = user.picks.filter(has_happened=has_happened)
        else:
            return Pick.objects.none()
    except (Buyer.DoesNotExist, Seller.DoesNotExist) as e:
        return Pick.objects.none()

    return picks


     
    
def get_all_pending_picks_for_buyer(buyer):
    return _get_picks(buyer.user, has_happened=False, user_type='buyer')

def get_all_processed_picks_for_buyer(buyer):
    return _get_picks(buyer.user, has_happened=True, user_type='buyer')

def get_all_pending_picks_for_seller(seller):
    return _get_picks(seller.user, has_happened=False, user_type='seller')

def get_all_processed_picks_for_seller(seller):
    return _get_picks(seller.user, has_happened=True, user_type='seller')

