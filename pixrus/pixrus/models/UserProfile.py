import uuid
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)
    meta_data = models.JSONField(null=True, blank=True)  # Shared metadata field

    class Meta:
        abstract = True  # Makes this an abstract base class