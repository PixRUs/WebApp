from django.db import models
from django.contrib.auth.models import User

class UserSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='session')
    last_logged_in = models.DateTimeField(null=True, blank=True)
    is_online = models.BooleanField(default=False)
