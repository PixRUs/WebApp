
from product.models import HistoricalPick, ActivePick
import heapq
import math
from pixrus.utils.probabilty_calculator import get_probability

from seller.models import Seller

type_of_pick_map = {
    "nba_basketball":1,
    "ncaa_basketball":2,
}
def get_recommended_picks(buyer,num_of_picks):
    """
    Returns recommended sellers based on a specific buyer
    The recommendations are based of the risk taken by buyer, type of sport, league and
    """

    ##Assign a value for the type of rist taken.
    average_amount_of_units, average_pick_risk, average_type_of_pick = calculate_buyer_averages(buyer)

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
    average_amount_of_units, average_pick_risk, average_type_of_pick = calculate_buyer_averages(buyer)
    class Seller_Value:
        def __init__(self, dist, seller):
            self.dist = dist
            self.seller = seller

        def __lt__(self, other):
            return self.dist < other.dist

    all_active_sellers = Seller.objects.all()
    pq = []
    for seller in all_active_sellers:
        risk, type, units = calculate_seller_averages(seller)
        distance = calculate_distance(risk_1=average_pick_risk,units_1=average_amount_of_units,type_of_pick_1=average_type_of_pick,units_2=units,type_of_pick_2=type,risk_2=risk)
        heapq.heappush(pq,Seller_Value(distance,seller))

    sellers = []
    k = heapq.nsmallest(min(num_of_sellers,all_active_sellers.count()), pq)
    for m in k:
        sellers.append(m.seller)
    return sellers

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



def calculate_buyer_averages(buyer):
    all_historical_picks  = buyer.historical_pick_buyer.all()
    return calculate_averages(all_historical_picks)

def calculate_seller_averages(seller):
    all_historical_seller_picks  = HistoricalPick.objects.filter(seller=seller)
    return calculate_averages(all_historical_seller_picks)


def calculate_averages(all_historical_picks):
    total_risk_value = 0
    total_picks = all_historical_picks.count()
    type_of_pick = 0
    amount_of_units = 0

    for pick in all_historical_picks:
        sport = pick.game_event_result.get('sport', 'basketball')
        league = pick.game_event_result.get('league', 'nba')
        pick_prob, type, units = calculate_pick_values(category=[sport, league], pick_data=pick.pick_data,
                                                       game_data=pick.game_event_result)
        total_risk_value += pick_prob
        amount_of_units += units
        type_of_pick += type

    if total_picks == 0:
        return 0,0,0
    average_amount_of_units = amount_of_units / total_picks
    average_pick_risk = total_risk_value / total_picks
    average_type_of_pick = type_of_pick / amount_of_units
    return average_amount_of_units, average_pick_risk, average_type_of_pick