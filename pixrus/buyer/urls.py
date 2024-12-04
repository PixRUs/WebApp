from django.urls import path
from . import views


urlpatterns = [
    path('dashboard/', views.buyer_landing, name='buyer_dashboard'),
    path('recommended/', views.buyer_recommended, name='buyer_recommended'),
    path('market/', views.market, name='market'),

]
