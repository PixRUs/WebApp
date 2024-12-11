import uuid
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import  Literal
from enum import Enum

class Seller(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='%(class)s_profile')
    profile_picture = models.ImageField(upload_to="profile_pics/", default="profile_pics/default.jpg")
    bio = models.TextField(max_length=500, blank=True, null=True)
    meta_data = models.JSONField(null=True, blank=True)


