from django.contrib import admin
from .models import Seller, Buyer, Pick, Subscription

admin.site.register(Seller)
admin.site.register(Buyer)
admin.site.register(Pick)
admin.site.register(Subscription)
