from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import ProfileCompletionForm
from buyer.models import Buyer
from seller.models import Seller
from django.views.decorators.cache import never_cache


# Landing page or any publicly accessible entry point
def landing(request):
    return render(request, 'index.html')

# Redirect directly to Google login
def login_view(request):
    # Redirect to tshe Google login URL
    return redirect('google_login')


@login_required
def home(request):
    # Check if the user is associated with the Buyer model
    if Buyer.objects.filter(user=request.user).exists():
        return redirect('buyer_dashboard')  # Replace with the actual buyer dashboard URL name
    # Check if the user is associated with the Seller model
    elif Seller.objects.filter(user=request.user).exists():
        return redirect('seller_dashboard')  
    return redirect('profile_completion')

@never_cache
@login_required
def profile_completion(request):
    if Buyer.objects.filter(user=request.user).exists():
        return redirect('buyer_dashboard')  # Replace with the actual buyer dashboard URL name
    # Check if the user is associated with the Seller model
    elif Seller.objects.filter(user=request.user).exists():
        return redirect('seller_dashboard')  # Replace with the actual seller dashboard URL name  
    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            user_name = form.cleaned_data.get('username')
            if role == 'seller':
                Seller.objects.get_or_create(user=request.user,
                defaults={'user_name': user_name,
                'meta_data': {}}
                )
                return redirect('seller_dashboard')  # Redirect to seller dashboard
            elif role == 'buyer':
                Buyer.objects.get_or_create(user=request.user,
                defaults={'user_name':user_name,
                'meta_data':{},
                'stats':{}}
                )
                return redirect('buyer_dashboard')  # Redirect to buyer dashboard
        else:
            # Show errors if form is invalid
            return render(request, 'profile_completion.html', {'form': form})

    else:
        form = ProfileCompletionForm()  # Display an empty form for GET requests
        return render(request, 'profile_completion.html', {'form': form})
