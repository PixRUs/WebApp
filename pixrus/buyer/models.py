import uuid
from django.db import models
from django.contrib.auth.models import User

class Buyer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='%(class)s_profile')
    meta_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()







