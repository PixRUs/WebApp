from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.seller_landing, name='seller_dashboard'),
    path('/post_pick',views.post_pick_view, name='post_pick'),
]
