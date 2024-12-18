from django.urls import path , include
from accounts.views import home, landing, profile_completion
from social_django.urls import urlpatterns as social_auth_urls

urlpatterns = [
    path('', landing, name='landing'),  # Landing page (accessible without login)
    path('home/', home, name='home'),   # Home page (requires login)
    path('profile-completion/',profile_completion, name='profile_completion'),
]