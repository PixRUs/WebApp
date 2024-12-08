from django.shortcuts import render
from pixrus.utils.decorators import role_required
from product.models import ActivePick, HistoricalPick,Subscription
from buyer.models import Buyer
from .recomendation.util import get_recommended_picks,get_recommended_sellers
from django.utils import timezone
from leaderboard.top import get_top_sellers
from seller.models import Seller, Stat

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

    seller_stat = []
    for seller in sellers:
        total_units_won = Stat.objects.filter(
            seller=seller, time_period="all_time", stat_name="total_units_won"
        ).first().stat_value
        total_number_of_success = Stat.objects.filter(
            seller=seller, time_period="all_time", stat_name="number_of_successes"
        ).first().stat_value
        number_of_picks_placed = Stat.objects.filter(
            seller=seller, time_period="all_time", stat_name="total_picks_placed"
        ).first().stat_value
        subscriber_count =  Subscription.objects.filter(seller=seller, subscribed_until__gt=timezone.now()).count()
        seller_stat.append((total_units_won, total_number_of_success, number_of_picks_placed, subscriber_count,seller))
    #top_5_active_picks = get_recommended_picks(buyer,5)


    context = {
        'buyer': buyer,
        'seller_picks': all_active,
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
    top_three_seller_units_won_past_week =get_top_sellers(time_unit="weekly",stat_name='total_units_won',n=3)
    top_three_successful_bets_won_past_week =get_top_sellers(time_unit="weekly",stat_name='number_of_successes',n=3)
    top_three_safest_sellers_past_week =get_top_sellers(time_unit="weekly",stat_name="total_probability",n=3,riskiest=True)
    top_three_riskiest_sellers_past_week =get_top_sellers(time_unit="weekly",stat_name="total_probability",n=3,riskiest=False)

    top_three_seller_units_won_past_month =get_top_sellers(time_unit="monthly",stat_name='total_units_won',n=3)
    top_three_successful_bets_won_past_month =get_top_sellers(time_unit="monthly",stat_name='number_of_successes',n=3)
    top_three_safest_sellers_past_month =get_top_sellers(time_unit="monthly",stat_name="total_probability",n=3,riskiest=True)
    top_three_riskiest_sellers_past_month =get_top_sellers(time_unit="monthly",stat_name="total_probability",n=3,riskiest=False)

    top_5_active_picks = get_recommended_picks(buyer,5)
    top_five_active_sellers = get_recommended_sellers(buyer,5)

    context = {'top_three_seller_units_won_past_week': top_three_seller_units_won_past_week,'top_three_successful_bets_won_past_week': top_three_successful_bets_won_past_week,
               "top_three_safest_sellers_past_week":top_three_safest_sellers_past_week,"top_three_riskiest_sellers_past_week":top_three_riskiest_sellers_past_week,
               "top_three_seller_units_won_past_month":top_three_seller_units_won_past_month,
               "top_three_successful_bets_won_past_month":top_three_successful_bets_won_past_month,
               "top_three_safest_sellers_past_month":top_three_safest_sellers_past_month,
               "top_three_riskiest_sellers_past_month":top_three_riskiest_sellers_past_month,
               "recommended_sellers": top_five_active_sellers,
               }

    return render(request, 'market_new.html',context)
