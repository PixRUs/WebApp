from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps
from buyer.models import Buyer
from seller.models import Seller

def role_required(required_role=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Redirect unauthenticated users
            if not request.user.is_authenticated:
                return redirect('userlogin')  # Redirect to login page

            # Check user's role
            is_seller = Seller.objects.filter(user=request.user).exists()
            is_buyer = Buyer.objects.filter(user=request.user).exists()

            if not (is_seller or is_buyer):
                return redirect('profile_completion')  # Redirect if no role assigned

            if required_role == 'seller' and not is_seller:
                return HttpResponseForbidden("You do not have permission to access this page.")
            if required_role == 'buyer' and not is_buyer:
                return HttpResponseForbidden("You do not have permission to access this page.")

            # Proceed with the view
            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator
