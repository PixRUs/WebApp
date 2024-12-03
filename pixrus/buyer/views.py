from django.shortcuts import render
from pixrus.utils.decorators import role_required
from product.models import ActivePick, HistoricalPick,Subscription
from buyer.models import Buyer
from seller.views import active_picks
from .recomendation.util import get_recommended_picks,get_recommended_sellers
from django.utils import timezone

@role_required(required_role='buyer')
def buyer_landing(request):
    buyer = Buyer.objects.get(user=request.user)
    subscriptions = Subscription.objects.filter(buyer=buyer)
    sellers = []
    for subscription in subscriptions:
        if subscription.subscribed_until > timezone.now():
            sellers.append(subscription.seller)
    all_active = []
    for seller in sellers:
        curr_active = ActivePick.objects.filter(seller=seller)
        for pick in curr_active:
            all_active.append((pick,seller))

    ##top_5_active_picks = get_recommended_picks(buyer,5)


    context = {
        'buyer': buyer,
        'seller_picks': all_active,
        'sellers': sellers,

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

