from django.shortcuts import render
from pixrus.utils.decorators import role_required
from product.models import ActivePick, HistoricalPick
from buyer.models import Buyer

@role_required(required_role='buyer')
def buyer_landing(request):
    buyer = Buyer.objects.get(user=request.user)
    active_picks = ActivePick.get_active_picks_for_buyer(buyer)
    historical_picks = HistoricalPick.get_historical_picks_for_buyer(buyer)
    context = {
        'buyer': buyer,
        'active_picks': active_picks,
        'historical_picks': historical_picks,
    }
    return render(request, 'buyer_landing.html',context)

