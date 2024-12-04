from django.contrib import admin
from .models import Seller,Stat  # Import the models from the same app

admin.site.register(Seller)
admin.site.register(Stat)
    # Register each model individually
