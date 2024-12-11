from django.db.models import Avg
from django.shortcuts import render
from pixrus.utils.decorators import role_required
from product.models import ActivePick, Subscription, HistoricalPick
from buyer.models import Buyer
from .recomendation.util import get_recommended_picks,get_recommended_sellers
from django.utils import timezone
from leaderboard.top import get_top_sellers
from pixrus.utils.stat import get_stats
from seller.utils.current_pick_data import get_current_pick_data

@role_required(required_role='buyer')
def buyer_landing(request):
    buyer = Buyer.objects.get(user=request.user)
    subscriptions = Subscription.objects.filter(buyer=buyer)
    sellers = []
    for subscription in subscriptions:
        if subscription.subscribed_until > timezone.now():
            sellers.append(subscription.seller)

    all_active = ActivePick.objects.filter(seller__in=sellers)
    picks = get_current_pick_data(all_active)

    seller_stat = []
    for seller in sellers:
        seller_stats = get_stats(seller,0)
        subscriber_count =  Subscription.objects.filter(seller=seller, subscribed_until__gt=timezone.now()).count()
        seller_stat.append((seller_stats, subscriber_count,seller))
    #top_5_active_picks = get_recommended_picks(buyer,5)




    context = {
        'buyer': buyer,
        'seller_picks': picks,
        'seller_stat': seller_stat,
    }

    return render(request, 'buyer_landing_new.html',context)
@role_required(required_role='buyer')
def buyer_recommended(request):
    buyer = Buyer.objects.get(user=request.user)
    top_5_active_picks = get_recommended_picks(buyer,5)
    top_five_active_sellers = get_recommended_sellers(buyer,5)
    print(top_5_active_picks)
    context = {'recommended_picks': top_5_active_picks,'sellers': top_five_active_sellers}
    return render(request, 'buyer_recommended.html',context)

@role_required(required_role='buyer')
def market(request):
    """Rising sellers, recommended free picks, recommended free sellers. and free active picks. """
    #sellers ==
    #sellers that have the most units won in the past week, month and year.
    #sellers that have the most successful bets in the past week month and year.
    #Sellers that have taken the safes bets.
    #sellers that have taken the riskiest bets.

    buyer = Buyer.objects.get(user=request.user)
    get_top_month = get_top_sellers(30,3)
    top_three_seller_units_won_past_month = get_top_month["sellers_with_most_number_of_units_made"]
    print(top_three_seller_units_won_past_month)
    top_three_successful_bets_won_past_month = get_top_month["sellers_with_most_number_of_successful_bets"]
    top_three_safest_sellers_past_month = get_top_month["safest_sellers"]
    top_three_riskiest_sellers_past_month = get_top_month["riskiest_sellers"]

    get_top_weekly = get_top_sellers(7,5)
    top_three_seller_units_won_past_week = get_top_weekly["sellers_with_most_number_of_units_made"]
    top_three_safest_sellers_past_week = get_top_weekly["safest_sellers"]
    top_three_riskiest_sellers_past_week = get_top_weekly["riskiest_sellers"]
    top_three_successful_bets_won_past_week = get_top_weekly["sellers_with_most_number_of_successful_bets"]

    top_5_active_picks = get_recommended_picks(buyer,5)
    top_five_active_sellers = get_recommended_sellers(buyer,5)

    recommended_sellers = []
    for seller in top_five_active_sellers:
        picks_sold = HistoricalPick.objects.filter(seller = seller).count()
        if picks_sold  == 0:
            success_rate = 0
            average_odds = 0
        else:
            success_rate = HistoricalPick.objects.filter(seller = seller,did_seller_succeed = True).count()/ picks_sold
            average_odds = HistoricalPick.objects.filter(seller=seller).aggregate(average_probability=Avg('probability'))['average_probability']
        recommended_sellers.append((picks_sold,success_rate,average_odds,seller ))

    context = {'top_three_seller_units_won_past_week': top_three_seller_units_won_past_week,'top_three_successful_bets_won_past_week': top_three_successful_bets_won_past_week,
               "top_three_safest_sellers_past_week":top_three_safest_sellers_past_week,"top_three_riskiest_sellers_past_week":top_three_riskiest_sellers_past_week,
               "top_three_seller_units_won_past_month":top_three_seller_units_won_past_month,
               "top_three_successful_bets_won_past_month":top_three_successful_bets_won_past_month,
               "top_three_safest_sellers_past_month":top_three_safest_sellers_past_month,
               "top_three_riskiest_sellers_past_month":top_three_riskiest_sellers_past_month,
               "recommended_sellers": recommended_sellers,
               }

    return render(request, 'market_new.html',context)
