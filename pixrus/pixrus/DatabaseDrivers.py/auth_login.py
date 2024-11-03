from django.contrib.auth.models import User
from django.utils import timezone
from models import Buyer, Seller, UserProfile, UserSession

def register_or_update_user(user_auth_data, user_meta_data, is_buyer):
    """
    Registers the user in the database, or updates their information based on metadata.
    """
    email = user_auth_data.get('email')
    first_name = user_auth_data.get('first_name')
    last_name = user_auth_data.get('last_name')
    google_id = user_auth_data.get('google_id')
    
    # Get or create the user
    user, created = User.objects.get_or_create(username=google_id, defaults={
        'email': email,  
        'first_name': first_name,
        'last_name': last_name,
    })
    
    # Get or create the user profile based on is_buyer flag
    if is_buyer:
        user_profile, _ = Buyer.objects.get_or_create(user=user, defaults={
            'meta_data': user_meta_data
        })
    else:
        user_profile, _ = Seller.objects.get_or_create(user=user, defaults={
            'meta_data': user_meta_data
        })
    update_user_session_login(user_profile=user_profile)

    return user_profile

def update_user_session_login(user_profile):
    """
    Updates the UserSession database when the user logs in.
    
    Args:
        user_profile (UserProfile): A user profile, either Buyer or Seller.
    """
    # Get or create the UserSession and update the timestamp and online status
    session, _ = UserSession.objects.get_or_create(user=user_profile.user)
    session.last_logged_in = timezone.now()
    session.is_online = True
    session.save()
    return session.id

def update_user_session_logout(user_profile):
    """
    Updates the UserSession database when the user logs out.

    Args:
        user_profile (UserProfile): A user profile, either Buyer or Seller.
    """
    try:
        session = UserSession.objects.get(user=user_profile.user)
        session.is_online = False
        session.save()
        return session.id
    except UserSession.DoesNotExist:
        return None  
