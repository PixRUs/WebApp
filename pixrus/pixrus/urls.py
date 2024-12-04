from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('seller/', include('seller.urls')),
    path('buyer/', include('buyer.urls')),
]
