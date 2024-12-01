
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
    all_historical_buyer_picks  = buyer.historical_pick_buyer.all()
    ##Assign a value for the type of rist taken.

    total_risk_value = 0
    total_picks = all_historical_buyer_picks.count()
    type_of_pick = 0
    amount_of_units = 0

    for pick in all_historical_buyer_picks:
        sport = pick.game_event_result['sport']
        league = pick.game_event_result['league']
        pick_prob,type,units = calculate_pick_values(category=[sport,league],pick_data=pick.pick_data,game_data=pick.game_event_result)
        total_risk_value += pick_prob
        amount_of_units += units
        type_of_pick += type

    average_amount_of_units = amount_of_units / total_picks
    average_pick_risk = total_risk_value / total_picks
    average_type_of_pick = type_of_pick / amount_of_units

    class Node:
        def __init__(self, dist, act_pick):
            self.dist = dist
            self.pick = act_pick

        def __lt__(self, other):
            return self.dist < other.dist
    all_active_picks = ActivePick.objects.filter(is_free=True)
    pq = []

    for active_pick in all_active_picks:
        sport = active_pick.game_data['sport']
        league = active_pick.game_data['league']
        risk,type,units = calculate_pick_values(category=[sport,league],pick_data=active_pick.pick_data,game_data=active_pick.game_data)
        distance = calculate_distance(risk_1=average_pick_risk,units_1=average_amount_of_units,type_of_pick_1=average_type_of_pick,units_2=units,type_of_pick_2=type,risk_2=risk)
        heapq.heappush(pq,Node(distance,active_pick))
    res = []
    k = heapq.nsmallest(min(num_of_picks,all_active_picks.count()), pq)
    for m in k:
        res.append(m.pick)
    return res



def get_probability(odd:str):
    if odd.startswith("-"):
        odd = odd[1:]
        odd = int(odd)
        return odd / (odd + 100)
    else:
        odd = int(odd)
        return 100 / (odd + 100)
    
def get_pick_category(sport,league):
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


def calculate_pick_values(category,pick_data,game_data):
    if type== 'h2h':
        pick_prob = get_probability(pick_data['odds'])
    else:
        pick_prob = 0.5
    category_val = get_pick_category(sport = category[0],league = category[1])
    amount_of_units = int(pick_data['bet_amount'])
    return pick_prob,category_val,amount_of_units
