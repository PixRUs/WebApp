from allauth.account.forms import SignupForm, LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


# Create your views here.
def signup_view(request):
    form = SignupForm(request.POST)  # Bind data from the request
    if form.is_valid():
        form.save(request)  # Save the user
        messages.success(request, 'Your account has been created!')
        return redirect('userlogin')  # Redirect to the login page or any other page
    else:
        form = SignupForm()  # Create new instance of the form

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    form = LoginForm()
    return render(request, 'login.html', {'form': form})


def landing(request):
    return render(request, 'landing.html')


@login_required
def home(request):
    return render(request, 'home.html', {'user': request.user})
