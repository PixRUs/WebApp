from django.contrib import admin
from .models import Buyer  # Import the models from the same app

admin.site.register(Buyer)  # Register each model individually
