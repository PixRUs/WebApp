import uuid
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='%(class)s_profile')
    created_at = models.DateTimeField(auto_now_add=True)
    meta_data = models.JSONField(null=True, blank=True)  # Shared metadata field


    class Meta:
        abstract = True  # Makes this an abstract base class

    @classmethod
    def get_by_email(cls, email):
        return cls.objects.get(user__email=email)

class Buyer(UserProfile,models.Model):
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
    @classmethod
    def get_store_name(cls, id=None, email=None):
        if not (id or email):  # Ensure at least one identifier is provided
            raise ValueError("You must provide either 'id' or 'email'.")

        if id:
            seller = cls.objects.get(id=id)
        else:
            seller = cls.get_by_email(email=email)
        
        return seller.store_name
