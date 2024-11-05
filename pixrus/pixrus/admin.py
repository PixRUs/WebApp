from django.contrib import admin
from .database_service.models import Seller, Buyer, Pick, Subscription

admin.site.register(Seller)
admin.site.register(Buyer)
admin.site.register(Pick)
admin.site.register(Subscription)
