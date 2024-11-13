from django.contrib import admin
from .models import ActivePick,HistoricalPick  # Import the models from the same app

admin.site.register(ActivePick) 
admin.site.register(HistoricalPick)
 # Register each model individually
