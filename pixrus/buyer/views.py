from django.shortcuts import render
from pixrus.utils.decorators import role_required
from product.models import ActivePick, HistoricalPick
from buyer.models import Buyer
from .recomendation.util import get_recommended_picks,get_recommended_sellers
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
@role_required(required_role='buyer')
def buyer_recommended(request):
    buyer = Buyer.objects.get(user=request.user)
    top_5_active_picks = get_recommended_picks(buyer,5)
    top_five_active_sellers = get_recommended_sellers(buyer,5)
    print(top_5_active_picks)
    context = {'recommended_picks': top_5_active_picks,'sellers': top_five_active_sellers}
    return render(request, 'buyer_recommended.html',context)

