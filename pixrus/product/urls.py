from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace_landing, name='marketplace_landing'),
]
