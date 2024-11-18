from django.urls import path
from accounts.views import home, landing, profile_completion

urlpatterns = [
    path('', landing, name='landing'),  # Landing page (accessible without login)
    path('home/', home, name='home'),   # Home page (requires login)
    path('profile-completion/',profile_completion, name='profile_completion'),
]