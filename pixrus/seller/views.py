from django.shortcuts import render
from product.models import ActivePick,HistoricalPick
from pixrus.utils.decorators import role_required
from seller.models import Seller
from django.http import HttpResponseForbidden


@role_required(required_role='seller')
def seller_landing(request):
    if not Seller.objects.filter(user=request.user).exists():
        return HttpResponseForbidden("You do not have permission to access this page.")  # Raw 403 response
    
    # Retrieve the seller object associated with the user
    seller = Seller.objects.get(user=request.user)
    active_picks = ActivePick.objects.filter(seller=seller)
    historical_picks = HistoricalPick.objects.filter(seller=seller)
    context = {
        'seller': seller,
        'active_picks': active_picks,
        'historical_picks': historical_picks,
    }
    return render(request, 'seller_landing.html',context)

