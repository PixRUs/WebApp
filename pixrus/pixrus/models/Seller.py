import uuid
from django.db import models
from django.contrib.auth.models import User

class Seller(UserProfile):
    pass
 # Optional JSON field for additional seller data

    def __str__(self):
        return f"Seller: {self.store_name}"

    @classmethod
    def get_by_email(cls, email):
        return cls.objects.get(user__email=email)  # Fetch Seller by User's email

    @classmethod
    def get_store_name(cls, id=None, email=None):
        if not (id or email):  # Ensure at least one identifier is provided
            raise ValueError("You must provide either 'id' or 'email'.")

        if id:
            seller = cls.objects.get(id=id)
        else:
            seller = cls.objects.get(user__email=email)
        
        return seller.store_name
