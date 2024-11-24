from django.shortcuts import render
from django.views.decorators.cache import never_cache

from product.models import ActivePick,HistoricalPick
from pixrus.utils.decorators import role_required
from seller.models import Seller
from django.http import HttpResponseForbidden,HttpResponse,JsonResponse
from .utils.pick_data_getter import get_odds

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
    return render(request, 'seller_landing.html',context)


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
                     "book_maker": request.POST.get("bookmaker")}
        game_data = {"team_1": request.POST.get("team_1"), "team_2": request.POST.get("team_2")}
        ActivePick.objects.create(seller=seller,event_start=request.POST.get("commence_time"),pick_data=pick_data,game_data=game_data,type_of_pick="h2h")
        return JsonResponse({"success": True, "message": "Pick activated successfully!"})
    else:
        return render(request,"activate_pick.html",{"pick":pick})

    #need to gather all the current pick info.


