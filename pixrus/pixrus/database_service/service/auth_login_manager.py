from django.contrib.auth.models import User
from django.utils import timezone
from  pixrus.database_service.models.UserProfile import Buyer,Seller,UserSession,UserProfile

def register_or_update_user(user_auth_data, user_meta_data, type_of_user):
    """
    Registers the user in the database, or updates their information based on metadata.
    
    Args: 
        user_auth_data (JSON): user auth data
        user_meta_data (JSON): user meta data
        type (String): pretaining the type of user sigining in   
    """
    email = user_auth_data.get('email')
    first_name = user_auth_data.get('first_name')
    last_name = user_auth_data.get('last_name')
    google_id = user_auth_data.get('google_id')
    username = user_meta_data['username']
    
    # Get or create the user
    user, created = User.objects.get_or_create(email=email, defaults={  
        'first_name': first_name,
        'last_name': last_name,
        'username' : username,
    })
    updated = False 
    if user.first_name != first_name:
        user.first_name = first_name
        updated = True
    if user.last_name != last_name:
        user.last_name = last_name
        updated = True
    if user.username != username:
        user.username = username
        updated = True
    

    # Save only if updates were made
    if updated:
        user.save()
        
    user_profile = None
    # Get or create the user profile based on is_buyer flag
    if type_of_user == "buyer":
        user_profile, _ = Buyer.objects.get_or_create(user=user, defaults={
            'meta_data': user_meta_data
        })
    if type_of_user == "seller":
        user_profile, _ = Seller.objects.get_or_create(user=user, defaults={
            'meta_data': user_meta_data
        })
    update_user_session_login(user_profile=user_profile,google_id=google_id,user_meta_data=user_meta_data)
    return user_profile, created 

def update_user_session_login(user_profile:UserProfile,google_id=None,user_meta_data=None):
    """
    Updates the UserSession database when the user logs in.
    
    Args:
        user_profile (UserProfile): A user profile, either Buyer or Seller.
    """
    updated = False 
    if google_id and user_profile.google_id != google_id:
        user_profile.google_id = google_id
        updated = True

    if user_meta_data and user_meta_data != user_profile.meta_data:
        user_profile.meta_data = user_meta_data
        updated = True

    # Save only once if there were updates
    if updated:
        user_profile.save()

    # Get or create the UserSession and update the timestamp and online status
    session, _ = UserSession.objects.get_or_create(user=user_profile.user)
    session.last_logged_in = timezone.now()
    session.is_online = True
    session.save()
    return session.id

def update_user_session_logout(user_profile:UserProfile):
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
