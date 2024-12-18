from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('dashboard/', views.seller_landing, name='seller_dashboard'),
    path('post_pick/<uuid:data_id>',views.post_pick_view, name='post_pick'),
    path('activate_pick/<str:pick_id>/', views.activate_pick, name='activate_pick'),
    path('active_picks/<uuid:seller_id>/', views.active_picks, name='active_picks'),
    path('historical_picks/<uuid:seller_id>/', views.historical_picks, name='historical_picks'),
    path('manage_buyers/', views.manage_buyers, name='manage_buyers'),
    path('view/<uuid:seller_id>',views.profile_view, name='profile_view'),
    path('subscribe/<uuid:seller_id>',views.subscribe, name='subscribe_view'),
    path('lookup',views.look_up, name='lookup'),
    path('search/', views.seller_search, name='seller_search'),
    path('update-pick/<uuid:pick_id>/',views.update_pick, name='update_pick'),
    path('manage/<uuid:seller_id>',views.manage_seller, name='manage_seller'),
    path('<uuid:seller_id>/delete', views.delete_seller, name='delete_seller'),
    path('logout/', auth_views.LogoutView.as_view(), name='auth_logout'),
]