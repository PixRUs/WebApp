import time

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.shortcuts import redirect

from buyer.models import Buyer
from product.models import ActivePick,HistoricalPick,ApiRequest
from pixrus.utils.decorators import role_required,access_required
from seller.models import Seller
from django.http import HttpResponseForbidden,JsonResponse,HttpResponseNotFound
from .utils.pick_data_getter import get_odds
from .forms import Subscription as SubscriptionForm,LookUp
from product.models import Subscription as Subscription
from .models import Stat
from .utils.analytics import get_new_subs,get_total_subs

@never_cache
@role_required(required_role='seller')
def seller_landing(request):
    if not Seller.objects.filter(user=request.user).exists():
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    # Retrieve the seller object associated with the user
    seller = Seller.objects.get(user=request.user)
    active_picks = ActivePick.objects.filter(seller=seller)
    historical_picks = HistoricalPick.objects.filter(seller=seller)
    all_time_stats = Stat.objects.filter(seller=seller,time_period = "all_time")
    monthly = Stat.objects.filter(seller=seller,time_period = "monthly")
    weekly = Stat.objects.filter(seller=seller,time_period = "weekly")

    all_time_placed = Stat.objects.filter(seller=seller,time_period = "all_time",stat_name="total_picks_placed").first().stat_value
    monthly_placed = Stat.objects.filter(seller=seller,time_period = "monthly",stat_name="total_picks_placed").first().stat_value
    weekly_placed = Stat.objects.filter(seller=seller,time_period = "weekly",stat_name="total_picks_placed").first().stat_value
    for stat in all_time_stats:
        if stat.stat_name == "total_probability":
            stat.stat_value = stat.stat_value / all_time_placed

    for stat in monthly:
        if stat.stat_name == "total_probability":
            stat.stat_value = stat.stat_value / all_time_placed
    for stat in weekly:
        if stat.stat_name == "total_probability":
            stat.stat_value = stat.stat_value / all_time_placed


    new_subs_chart_data = get_new_subs(seller)
    total_subs = get_total_subs(seller)

    context = {
        'seller': seller,
        'active_picks': active_picks,
        'historical_picks': historical_picks,
        'all_time_stats':all_time_stats,
        'monthly':monthly,
        'weekly':weekly,
        "chart_data": new_subs_chart_data,
        "total_subscribers":total_subs
    }
    return render(request, 'seller_page.html', context)


@role_required(required_role='seller')
def post_pick_view(request,data_id):
    if not Seller.objects.filter(user=request.user).exists():
        return HttpResponseForbidden("You do not have permission to access this page.")


    # Get current filter parameters or defaults
    team_filter = request.GET.get("team", request.session.get("team_filter", "")).lower()
    sportsbook_filter = request.GET.get("sportsbook", request.session.get("sportsbook_filter", "")).lower()
    date_filter = request.GET.get("date", request.session.get("date_filter", "")).lower()


    # Store filters in session for persistence
    request.session["team_filter"] = team_filter
    request.session["sportsbook_filter"] = sportsbook_filter
    request.session["date_filter"] = date_filter

    api_req = ApiRequest.objects.get(id=data_id)
    current_pick_data = api_req.response_data["games"]

    request.session["odds"] = api_req.response_data

    filtered_picks = []
    unique_sportsbooks = set()

    # Extract unique sportsbooks
    for pick in current_pick_data:
        for bookmaker in pick["bookmakers"]:
            unique_sportsbooks.add(bookmaker["title"])

    # Apply filters
    for pick in current_pick_data:
        # Check team filter
        if team_filter and team_filter not in pick["home_team"].lower() and team_filter not in pick[
            "away_team"].lower():
            continue

        # Check date filter
        if date_filter and not pick["commence_time"].startswith(date_filter):
            continue

        # Check sportsbook filter
        if sportsbook_filter:
            matching_bookmakers = [
                bookmaker for bookmaker in pick["bookmakers"]
                if sportsbook_filter in bookmaker["title"].lower()
            ]
            if not matching_bookmakers:
                continue
            pick["bookmakers"] = matching_bookmakers

        filtered_picks.append(pick)

    context = {
        "picks": filtered_picks,
        "all_picks": current_pick_data,
        "unique_sportsbooks": sorted(unique_sportsbooks),
    }

    return render(request, "post_pick.html", context)


@role_required(required_role='seller')
def activate_pick(request, pick_id):
    seller_query = Seller.objects.filter(user=request.user)
    if not seller_query:
        return HttpResponseForbidden("You do not have permission to access this page.")

    try:
        picks = request.session['odds']['games']
        sport = request.session['odds']['sport']
        type_of_pick = request.session['odds']['type']
        league = request.session['odds']['league']
    except KeyError:
        messages.error(request, "Session data is missing or invalid.")
        return redirect('seller_dashboard')

    pick = next((pick for pick in picks if pick["id"] == pick_id), None)
    if not pick:
        messages.error(request, "Pick not found.")
        return redirect('seller_dashboard')

    seller = seller_query.first()

    if request.method == "POST":
        required_fields = ["outcome", "multiplier", "bookmaker", "unit_size", "home_team", "away_team", "commence_time"]
        missing_fields = [field for field in required_fields if not request.POST.get(field)]
        if missing_fields:
            messages.error(request, f"Missing fields: {', '.join(missing_fields)}")
            return redirect('seller_dashboard')

        pick_data = {
            "target_winner": request.POST["outcome"],
            "odds": request.POST["multiplier"],
            "book_maker": request.POST["bookmaker"],
            "bet_amount": request.POST["unit_size"],
            "type": request.POST["type"],
        }
        game_data = {
            "home_team": request.POST["home_team"],
            "away_team": request.POST["away_team"],
            "sport": sport,
            "league": league,
        }

        ActivePick.objects.create(
            seller=seller,
            event_start=request.POST["commence_time"],
            pick_data=pick_data,
            game_data=game_data,
            type_of_pick=type_of_pick,
        )


        return redirect('seller_dashboard')
    return render(request, "activate_pick.html", {"pick": pick})


@login_required
@access_required()
def active_picks(request,seller_id):
    try:
        seller = Seller.objects.get(id=seller_id)
    except Seller.DoesNotExist:
        return HttpResponseNotFound("Seller not found")


    active_picks = ActivePick.objects.filter(seller=seller)
    paginator = Paginator(active_picks, 10)

    # Get the current page number from the request
    page_number = request.GET.get('page', 1)
    picks_page = paginator.get_page(page_number)

    return render(request, 'seller_current_picks.html', {
        'picks_page': picks_page,"active_picks":active_picks
    })

@login_required
@access_required()
def historical_picks(request, seller_id):
    try:
        seller = Seller.objects.get(id=seller_id)
    except Seller.DoesNotExist:
        return HttpResponseNotFound("Seller not found")

    historical_picks = HistoricalPick.objects.filter(seller=seller)  # Query for active picks
    paginator = Paginator(historical_picks, 10)  # Show 10 picks per page

    # Get the current page number from the request
    page_number = request.GET.get('page', 1)
    picks_page = paginator.get_page(page_number)

    return render(request, 'seller_prev_picks.html', {
        'picks_page': picks_page
    })

@role_required(required_role='seller')
def manage_buyers(request):
    if not Seller.objects.filter(user=request.user).exists():
        return HttpResponseForbidden("You do not have permission to access this page.")

    # Retrieve the seller object associated with the user
    seller = Seller.objects.get(user=request.user)
    subscriber_queries = Subscription.objects.filter(seller=seller)
    terminated_subscriptions = []
    active_subscriptions = []
    for sub in subscriber_queries:
        if sub.subscribed_until < timezone.now():
            terminated_subscriptions.append(sub)
        else:
            active_subscriptions.append(sub)

    single_pick_buyers = []
    active_picks = ActivePick.objects.filter(seller=seller)
    for pick in active_picks:
        buyers = pick.buyers_with_access.all()  # Fetch all buyers for this pick
        single_pick_buyers.append((buyers, pick))  # Append as a tuple (pick, buyers)

    historical_picks = HistoricalPick.objects.filter(seller=seller)
    for pick in historical_picks:
        buyers = pick.buyers_with_access.all()  # Fetch all buyers for this pick
        single_pick_buyers.append((buyers, pick))  # Append as a tuple (pick, buyers)

    # Result: List of tuples [(pick1, buyers_for_pick1), (pick2, buyers_for_pick2), ...]

    context = {"terminated_subscriptions": terminated_subscriptions, "active_subscriptions": active_subscriptions, "buyers": single_pick_buyers}
    return render(request, 'manage_buyers.html', context)

    #need to gather all the current pick info.


def profile_view(request,seller_id):
    try:
        seller = Seller.objects.get(id=seller_id)
    except Seller.DoesNotExist:
        return HttpResponseNotFound("Seller not found")
    try:
        buyer = Buyer.objects.get(user=request.user)
    except Buyer.DoesNotExist:
        buyer = None
    subscription = None
    curr_picks = None

    if buyer:
        is_buyer = True
        try:
            subscription = Subscription.objects.get(seller=seller,buyer=buyer)
        except Subscription.DoesNotExist:
            subscription = None

        if subscription and subscription.subscribed_until > timezone.now():
            curr_picks = ActivePick.objects.filter(seller=seller)
    else:
        is_buyer = False

    view_historical_picks = HistoricalPick.objects.filter(seller=seller).order_by('-posted_at')[:5]
    free_active_picks = ActivePick.objects.filter(seller=seller,is_free=True).order_by('-posted_at')

    all_time_stats = Stat.objects.filter(seller = seller,time_period = "all_time")
    monthly = Stat.objects.filter(seller = seller,time_period = "monthly")
    weekly = Stat.objects.filter(seller = seller,time_period = "weekly")

    context = {
        "seller": seller,
        "subscription": subscription,
        "active_picks" : curr_picks,
        "historical_picks" : view_historical_picks,
        "free_active_picks" : free_active_picks,
        "all_time_stats" : all_time_stats,
        "monthly" : monthly,
        "weekly" : weekly,
        "is_buyer": is_buyer
    }
    return render(request, 'profile_view.html', context)
@role_required(required_role="buyer")
def subscribe(request, seller_id):
    try:
        seller = Seller.objects.get(id=seller_id)
    except Seller.DoesNotExist:
        return HttpResponseNotFound("Seller not found")
    buyer = Buyer.objects.get(user=request.user)

    sub_until = None
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            selected_plan = form.cleaned_data['plan']
            if selected_plan =="yearly":
                sub_until = timezone.now() + relativedelta(years=1)
            elif selected_plan =="monthly":
                sub_until = timezone.now() + relativedelta(months=1)
            elif selected_plan =="weekly":
                sub_until = timezone.now() + relativedelta(weeks=1)
            elif selected_plan =="daily":
                sub_until = timezone.now() + relativedelta(days=1)

            Subscription.objects.get_or_create(buyer=buyer,seller=seller,defaults={'subscribed_until':sub_until})
            messages.success(request, f"Subscription Successful! You selected the {selected_plan} plan. You will now be redirected to the seller page")
            return redirect('profile_view', seller_id=seller_id)

    return render(request, 'initialize_subscription.html', {'seller': seller,'form': SubscriptionForm})

@role_required(required_role="seller")
def look_up(request):
    if request.method == 'POST':
        form = LookUp(request.POST)
        if form.is_valid():
            sports_league_choice = form.cleaned_data['sports_league_choice']
            form_type_of_bet = form.cleaned_data['type_of_bets']
            if sports_league_choice =="basketball_nba":
                if form_type_of_bet == "money_line":
                    api_obj = get_odds(sport="basketball", league="nba",type_of_pick='h2h')
                    return redirect('post_pick', api_obj.id)


    return render(request, 'look_up.html',{'form':LookUp})

def seller_search(request):
    query = request.GET.get('query', '')
    sellers = Seller.objects.filter(user_name__icontains=query)
    return render(request, 'search_results.html', {'query': query, 'sellers': sellers})


