from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/', views.buyer_landing, name='buyer_dashboard'),
]
