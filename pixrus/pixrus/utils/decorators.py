from django.utils import timezone

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps
from buyer.models import Buyer
from product.models import Subscription
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


def access_required():
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check user's role
            is_seller = Seller.objects.filter(user=request.user).exists()
            is_buyer = Buyer.objects.filter(user=request.user).exists()

            seller_id = kwargs.get('seller_id')
            try:
                seller_accessed = Seller.objects.get(id=seller_id)
            except Seller.DoesNotExist:
                return HttpResponseForbidden("You do not have permission to access this page.")

            if is_seller:
                try:
                    seller = Seller.objects.get(user=request.user.id)
                except Seller.DoesNotExist:
                    return HttpResponseForbidden("You do not have permission to access this page.")
                if seller != seller_accessed:
                    return HttpResponseForbidden("You do not have permission to access this page.")
            if is_buyer:
                buyer = Buyer.objects.get(user=request.user)
                try:
                    subscription = Subscription.objects.get(seller=seller_accessed, buyer=buyer)
                except Subscription.DoesNotExist:
                    return HttpResponseForbidden("You do not have permission to access this page.")
                if subscription.subscribed_until is None or subscription.subscribed_until < timezone.now():
                    return HttpResponseForbidden("You do not have permission to access this page.")

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator

