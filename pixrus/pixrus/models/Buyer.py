import uuid
from django.db import models

class Buyer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    email = models.CharField(max_length=50, null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_data = models.JSONField() 

    @classmethod
    def get_by_email(cls, email):
        return cls.objects.get(email=email)
    
    @classmethod
    def get_user_first_initialization(cls, id=None, email=None):
        if not (id or email):  # Checks that at least one is provided
            raise ValueError("You must provide either 'id' or 'email'.")
        
        if id:
            user = cls.objects.get(id=id)
        else:
            user = cls.objects.get(email=email)
        
        return f"{user.first_name} {user.last_name[0]}" 
    
    @classmethod
    def get_user_creation_date(cls, id=None, email=None):
        if not (id or email):  # Enforce that at least one must be provided
            raise ValueError("You must provide either 'id' or 'email'.")
        
        if id:
            user = cls.objects.get(id=id)
        else:
            user = cls.objects.get(email=email)
        
        return user.created_at




    