from django.contrib import admin
from .models import ActivePick,HistoricalPick,ApiRequest  # Import the models from the same app

admin.site.register(ActivePick) 
admin.site.register(HistoricalPick)
admin.site.register(ApiRequest)
 # Register each model individually
