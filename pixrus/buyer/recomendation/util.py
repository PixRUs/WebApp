from buyer.models import Buyer
from pixrus.tasks.update_pick_and_user_data import type_of_pick
from seller.models import Seller
from product.models import HistoricalPick, ActivePick
import heapq
import math

type_of_pick_map = {
    "nba_basketball":1,
    "ncaa_basketball":2,
}
def get_recommended_picks(buyer,num_of_picks):
    """
    Returns recommended sellers based on a specific buyer
    The recommendations are based of the risk taken by buyer, type of sport, league and
    """
    all_historical_buyer_picks  = buyer.active_picks_buyer_access.all()
    ##Assign a value for the type of rist taken.

    total_risk_value = 0
    total_picks = all_historical_buyer_picks.count()
    type_of_pick = 0
    amount_of_units = 0

    for pick in all_historical_buyer_picks:
        if pick.type_of_pick == 'h2h':
            total_risk_value += get_probability(pick.pick_data['odds'])
        else:
            total_risk_value += 0.5
        type_of_pick += get_type_of_pick(pick.game_event_result)
        amount_of_units += pick.pick_data['bet_amount']

    average_amount_of_units = amount_of_units / total_picks
    average_pick_risk = total_risk_value / total_picks
    average_type_of_pick = type_of_pick / amount_of_units

    class Node:
        def __init__(self, dist, pick):
            self.dist = dist
            self.pick = pick

        def __lt__(self, other):
            return self.dist < other.dist
    all_active_picks = ActivePick.objects.filter(is_free=True)
    pq = []
    for active_pick in all_active_picks:
        risk = get_probability(active_pick.pick_data['odds'])
        type = get_type_of_pick(active_pick.game_data)
        units = get_probability(active_pick.pick_data['bet_amount'])
        distance = calculate_distance(risk_1=average_pick_risk,units_1=average_amount_of_units,type_of_pick_1=average_type_of_pick,units_2=units,type_of_pick_2=type,risk_2=risk)
        heapq.heappush(pq,Node(distance,active_pick))
    return heapq.nsmallest(num_of_picks, pq), average_amount_of_units, average_pick_risk, average_type_of_pick

    

def get_probability(odd:str):
    if odd.startswith("-"):
        odd = odd[1:]
        odd = int(odd)
        return odd / (odd + 100)
    else:
        odd = int(odd)
        return 100 / (odd + 100)
def get_type_of_pick(game_event_result):
    sport = game_event_result['sport']
    league = game_event_result['league']
    return type_of_pick_map[league+"_"+sport]

def calculate_distance(risk_1,units_1,type_of_pick_1,risk_2,units_2,type_of_pick_2):
    """Euclidean distance"""
    return math.sqrt(
        (risk_2 - risk_1)**2 +
        (units_2 - units_1)**2 +
        (type_of_pick_2 - type_of_pick_1)**2
    )

def get_recommended_sellers(buyer, num_of_sellers):
    pass


def get_hottest_picks():
    pass



