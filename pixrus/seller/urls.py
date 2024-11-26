from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.seller_landing, name='seller_dashboard'),
    path('post_pick/',views.post_pick_view, name='post_pick'),
    path('activate_pick/<str:pick_id>/', views.activate_pick, name='activate_pick'),
    path('profile/<uuid:seller_id>/', views.profile, name='profile')
]
