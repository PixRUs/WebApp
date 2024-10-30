import uuid
from django.contrib.auth.models import User

class Buyer(UserProfile):
    pass

    @classmethod
    def get_user_name(cls, id=None, email=None):
        if not (id or email):  # Checks that at least one is provided
            raise ValueError("You must provide either 'id' or 'email'.")
        
        if id:
            user = cls.objects.get(id=id)
        else:
            user = cls.objects.get(user__email=email)  # Access email via User
        
        return f"{user.user.first_name} {user.user.last_name[0]}"  # Access first and last names via User
    
    @classmethod
    def get_user_creation_date(cls, id=None, email=None):
        if not (id or email):  # Enforce that at least one must be provided
            raise ValueError("You must provide either 'id' or 'email'.")
        
        if id:
            user = cls.objects.get(id=id)
        else:
            user = cls.objects.get(user__email=email)  # Access email via User
        
        return user.created_at
