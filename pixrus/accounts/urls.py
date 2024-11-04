from django.urls import path
from accounts.views import home, landing, login_view, signup_view

urlpatterns = [
    path('', landing, name='landing'),  # Landing page (accessible without login)
    path('home/', home, name='home'),   # Home page (requires login)
    path('userlogin/', login_view, name='userlogin'),
    path('usersignup/', signup_view, name='usersignup'),

]