from django.contrib import admin
from .models import Seller  # Import the models from the same app

admin.site.register(Seller)
    # Register each model individually
