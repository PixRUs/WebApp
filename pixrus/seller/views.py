import time

from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.shortcuts import redirect

from buyer.models import Buyer
from product.models import ActivePick,HistoricalPick,Subscription
from pixrus.utils.decorators import role_required
from seller.models import Seller
from django.http import HttpResponseForbidden,HttpResponse,JsonResponse,HttpResponseNotFound
from .utils.pick_data_getter import get_odds
from .forms import Subscription as SubscriptionForm
from product.models import Subscription as Subscription
@never_cache
@role_required(required_role='seller')
def seller_landing(request):
    if not Seller.objects.filter(user=request.user).exists():
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    # Retrieve the seller object associated with the user
    seller = Seller.objects.get(user=request.user)
    active_picks = ActivePick.objects.filter(seller=seller)
    historical_picks = HistoricalPick.objects.filter(seller=seller)
    context = {
        'seller': seller,
        'active_picks': active_picks,
        'historical_picks': historical_picks,
        'stats':seller.stats,
    }
    return render(request, 'seller_dashboard.html', context)


@role_required(required_role='seller')
def post_pick_view(request):
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


    current_pick_data = get_odds(sport="basketball", league="nba",type_of_pick='h2h')
    request.session["odds"] = current_pick_data

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
def activate_pick(request,pick_id):
    seller_query = Seller.objects.filter(user=request.user)
    if not seller_query:
        return HttpResponseForbidden("You do not have permission to access this page.")
    picks = request.session['odds']
    pick = next((pick for pick in picks if pick["id"] == pick_id), None)
    seller = seller_query.first()
    if request.method == "POST":
        pick_data = {"target_winner": request.POST.get("outcome"), "odds": request.POST.get("multiplier"),
                     "book_maker": request.POST.get("bookmaker"),"bet_amount": request.POST.get("unit_size")}
        game_data = {"home_team": request.POST.get("home_team"), "away_team": request.POST.get("away_team")}
        ActivePick.objects.create(seller=seller,event_start=request.POST.get("commence_time"),pick_data=pick_data,game_data=game_data,type_of_pick="h2h")
        return JsonResponse({"success": True, "message": "Pick activated successfully!"})
    else:
        return render(request,"activate_pick.html",{"pick":pick})


@role_required(required_role='seller')
def active_picks(request,seller_id):
    try:
        seller = Seller.objects.get(id=seller_id)
    except Seller.DoesNotExist:
        return HttpResponseNotFound("Seller not found")

    active_picks = ActivePick.objects.filter(seller=seller)  # Query for active picks
    paginator = Paginator(active_picks, 10)  # Show 10 picks per page

    # Get the current page number from the request
    page_number = request.GET.get('page', 1)
    picks_page = paginator.get_page(page_number)

    return render(request, 'seller_current_picks.html', {
        'picks_page': picks_page
    })

@role_required(required_role='seller')
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
        subscription = Subscription.objects.get(seller=seller,buyer=buyer)
        if subscription and subscription.subscribed_until > timezone.now():
            curr_picks = ActivePick.objects.filter(seller=seller)

    view_historical_picks = HistoricalPick.objects.filter(seller=seller).order_by('-posted_at')[:5]
    free_active_picks = ActivePick.objects.filter(seller=seller,is_free=True).order_by('-posted_at')
    context = {
        "seller": seller,
        "subscription": subscription,
        "active_picks" : curr_picks,
        "historical_picks" : view_historical_picks,
        "free_active_picks" : free_active_picks,
    }
    return render(request, 'profile_view.html', context)

def subscribe(request, seller_id):
    try:
        seller = Seller.objects.get(id=seller_id)
    except Seller.DoesNotExist:
        return HttpResponseNotFound("Seller not found")
    buyer = Buyer.objects.get(user=request.user)
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            selected_plan = form.cleaned_data['plan']
            if selected_plan =="yearly":
                subscribed_until = timezone.now() + relativedelta(years=1)
            elif selected_plan =="monthly":
                subscribed_until = timezone.now() + relativedelta(months=1)
            elif selected_plan =="weekly":
                subscribed_until = timezone.now() + relativedelta(weeks=1)
            elif selected_plan =="daily":
                subscribed_until = timezone.now() + relativedelta(days=1)

            Subscription.objects.get_or_create(buyer=buyer,seller=seller,defaults={'subscribed_until':subscribed_until})
            messages.success(request, f"Subscription Successful! You selected the {selected_plan} plan. You will now be redirected to the seller page")
            return redirect('profile_view', seller_id=seller_id)

    return render(request, 'initialize_subscription.html', {'seller': seller,'form': Subscription})




