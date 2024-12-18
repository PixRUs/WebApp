from product.models import HistoricalPick, ActivePick, Subscription
import heapq
import math
from pixrus.utils.probabilty_calculator import get_probability

from seller.models import Seller
from seller.views import historical_picks

type_of_pick_map = {
    "nba_basketball": 1,
    "ncaa_basketball": 2,
}

def get_recommended_picks(buyer, num_of_picks):
    """
    Returns recommended picks based on a specific buyer.
    Recommendations are based on the risk taken by the buyer, type of sport, league, etc.
    """
    average_amount_of_units, average_pick_risk, average_type_of_pick = calculate_buyer_averages(buyer)

    class Node:
        def __init__(self, dist, act_pick):
            self.dist = dist
            self.pick = act_pick

        def __lt__(self, other):
            return self.dist < other.dist

    all_active_picks = list(ActivePick.objects.filter(is_free=True))
    pq = []

    for active_pick in all_active_picks:
        sport = active_pick.game_data['sport']
        league = active_pick.game_data['league']
        risk, pick_type, units = calculate_pick_values(
            category=[sport, league], pick_data=active_pick.pick_data, type_of_bet= active_pick.type_of_pick, game_data=active_pick.game_data
        )
        distance = calculate_distance(
            risk_1=average_pick_risk,
            units_1=average_amount_of_units,
            type_of_pick_1=average_type_of_pick,
            units_2=units,
            type_of_pick_2=pick_type,
            risk_2=risk,
        )
        heapq.heappush(pq, Node(distance, active_pick))

    res = [node.pick for node in heapq.nsmallest(min(num_of_picks, len(all_active_picks)), pq)]
    return res


def get_pick_category(sport, league):
    return type_of_pick_map[league + "_" + sport]


def calculate_distance(risk_1, units_1, type_of_pick_1, risk_2, units_2, type_of_pick_2):
    """Calculate Euclidean distance."""
    return math.sqrt(
        (risk_2 - risk_1) ** 2 +
        (units_2 - units_1) ** 2 +
        (type_of_pick_2 - type_of_pick_1) ** 2
    )


def get_recommended_sellers(buyer, num_of_sellers):
    average_amount_of_units, average_pick_risk, average_type_of_pick = calculate_buyer_averages(buyer)

    class SellerValue:
        def __init__(self, dist, seller):
            self.dist = dist
            self.seller = seller

        def __lt__(self, other):
            return self.dist < other.dist

    all_active_sellers = list(Seller.objects.all())
    pq = []

    for seller in all_active_sellers:
        risk, pick_type, units = calculate_seller_averages(seller)
        distance = calculate_distance(
            risk_1=average_pick_risk,
            units_1=average_amount_of_units,
            type_of_pick_1=average_type_of_pick,
            units_2=units,
            type_of_pick_2=pick_type,
            risk_2=risk,
        )
        heapq.heappush(pq, SellerValue(distance, seller))

    sellers = [node.seller for node in heapq.nsmallest(min(num_of_sellers, len(all_active_sellers)), pq)]
    return sellers


def calculate_pick_values(category, pick_data, type_of_bet,  game_data):
    pick_prob = get_probability(pick_data['odds']) if type_of_bet == 'h2h' else 0.5
    category_val = get_pick_category(sport=category[0], league=category[1])
    amount_of_units = int(pick_data['bet_amount'])
    return pick_prob, category_val, amount_of_units


def calculate_buyer_averages(buyer):
    # Get all sellers from subscriptions
    sellers = [query.seller for query in Subscription.objects.filter(buyer=buyer)]

    # Get historical picks for all sellers and flatten the results

    all_historical_picks = HistoricalPick.objects.filter(seller__in=sellers)
    return calculate_averages(all_historical_picks)


def calculate_seller_averages(seller):
    all_historical_seller_picks = HistoricalPick.objects.filter(seller=seller)
    return calculate_averages(all_historical_seller_picks)


def calculate_averages(all_historical_picks):
    total_risk_value = 0
    total_picks = all_historical_picks.count()
    type_of_pick = 0
    amount_of_units = 0

    for pick in all_historical_picks:
        sport = pick.game_event_result.get('sport', 'basketball')
        league = pick.game_event_result.get('league', 'nba')
        pick_prob, pick_type, units = calculate_pick_values(
            category=[sport, league], pick_data=pick.pick_data, type_of_bet=pick.type_of_pick, game_data=pick.game_event_result
        )
        total_risk_value += pick_prob
        amount_of_units += units
        type_of_pick += pick_type

    if total_picks == 0 or amount_of_units == 0:
        return 0, 0, 0

    average_amount_of_units = amount_of_units / total_picks
    average_pick_risk = total_risk_value / total_picks
    average_type_of_pick = type_of_pick / total_picks
    return average_amount_of_units, round(average_pick_risk,2), average_type_of_pick
