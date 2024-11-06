import uuid
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='%(class)s_profile')
    created_at = models.DateTimeField(auto_now_add=True)
    meta_data = models.JSONField(null=True, blank=True)

    @classmethod
    def register_or_update_user(cls, user_auth_data, user_meta_data, type_of_user):
        email = user_auth_data.get('email')
        first_name = user_auth_data.get('first_name')
        last_name = user_auth_data.get('last_name')
        google_id = user_auth_data.get('google_id')
        username = user_meta_data['username']
        
        # Get or create the User instance
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
            }
        )

        # Update User instance if necessary
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

        if updated:
            user.save()
        
        # Create or get the appropriate UserProfile subtype (Buyer or Seller)
        if type_of_user == "buyer":
            user_profile, _ = Buyer.objects.get_or_create(user=user, defaults={'meta_data': user_meta_data})
        elif type_of_user == "seller":
            user_profile, _ = Seller.objects.get_or_create(user=user, defaults={'meta_data': user_meta_data})
        else:
            raise ValueError("Invalid user type specified.")
        
        # Update the session login information
        user_profile.update_user_session_login(google_id=google_id, user_meta_data=user_meta_data)
        
        return user_profile, created

    def update_user_session_login(self, google_id=None, user_meta_data=None):
        updated = False
        if google_id and self.google_id != google_id:
            self.google_id = google_id
            updated = True
        if user_meta_data and user_meta_data != self.meta_data:
            self.meta_data = user_meta_data
            updated = True

        if updated:
            self.save()

        # Update or create the session
        session, _ = UserSession.objects.get_or_create(user=self.user)
        session.last_logged_in = timezone.now()
        session.is_online = True
        session.save()
        return session.id

    def update_user_session_logout(self):
        try:
            session = UserSession.objects.get(user=self.user)
            session.is_online = False
            session.save()
            return session.id
        except UserSession.DoesNotExist:
            return None
    class Meta:
        abstract = True  # Makes this an abstract base class

    @classmethod
    def get_by_email(cls, email):
        return cls.objects.get(user__email=email)

class Buyer(UserProfile):
    # Buyer-specific fields (if any) can go here
    @classmethod
    def get_user_name(cls, id=None, email=None):
        if not (id or email):  # Ensure at least one identifier is provided
            raise ValueError("You must provide either 'id' or 'email'.")

        if id:
            user_profile = cls.objects.get(id=id)
        else:
            user_profile = cls.get_by_email(email=email)
        
        return f"{user_profile.user.first_name} {user_profile.user.last_name[0]}"

    @classmethod
    def get_user_creation_date(cls, id=None, email=None):
        if not (id or email):  # Ensure at least one identifier is provided
            raise ValueError("You must provide either 'id' or 'email'.")

        if id:
            user_profile = cls.objects.get(id=id)
        else:
            user_profile = cls.get_by_email(email=email)
        
        return user_profile.created_at

class Seller(UserProfile):
    pass

class UserSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='session')  # Use User directly
    last_logged_in = models.DateTimeField(null=True, blank=True)
    is_online = models.BooleanField(default=False)



