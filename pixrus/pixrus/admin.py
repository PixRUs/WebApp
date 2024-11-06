# admin.py
from django.contrib import admin
from .database_service.models.Products import ActivePick, HistoricalPick, VendorApiRequest, Subscription
from .database_service.models.UserProfile import Buyer, Seller, UserSession

# Registering each model directly
admin.site.register(ActivePick)
admin.site.register(HistoricalPick)
admin.site.register(VendorApiRequest)
admin.site.register(Subscription)
admin.site.register(Buyer)
admin.site.register(Seller)
admin.site.register(UserSession)
