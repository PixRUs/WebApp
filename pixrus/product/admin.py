from django.contrib import admin
from .models import ActivePick,HistoricalPick,ApiRequest,Subscription # Import the models from the same app

admin.site.register(ActivePick) 
admin.site.register(HistoricalPick)
admin.site.register(ApiRequest)
admin.site.register(Subscription)
 # Register each model individually
