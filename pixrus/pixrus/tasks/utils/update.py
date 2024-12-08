""" For now current stats is storing  number of successful picks, and number of unsuccesful picks. 
    Each time we just update the sellers. Need the implementation to be such that I wont have to change the whole structure if I were to add another statistic / sport.
"""
from seller.models import Stat
from decimal import Decimal

from pixrus.utils.probabilty_calculator import get_probability
def update_buyer_and_seller_stats(pick_data,result_data,seller,buyers,type_of_pick):
    """_summary_

    Args:
        result_data (json): should list the game winner, teams invloved. 
        pick_data (_type_): should list the pick who the 
        seller (_type_): seller associated with the pick. 
        buyers (_type_): buyers who have purchase the pick. 
    """
    bet_type_functions = {
        "h2h": update_seller_stats_h2h,
        "pointspread": update_seller_stats_pointspread,
    }
    bet_type_function = bet_type_functions.get(type_of_pick)
    if bet_type_function:
        return bet_type_function(seller, pick_data=pick_data, result_data=result_data)
    return False


def update_seller_stats_h2h(seller,pick_data,result_data):
    #Moneyline: Betting on the team or player to win the game outright, regardless of the score.
    stat_query = Stat.objects.filter(seller=seller)
    if result_based_of_game_win(pick_data=pick_data, event_result=result_data):
        for stat in stat_query:
            if stat.stat_name == "total_picks_placed":
                stat.stat_value += 1
            if stat.stat_name == "total_units_won":
                stat.stat_value += int(pick_data['bet_amount'])
            if stat.stat_name == "number_of_successes":
                stat.stat_value += 1
            if stat.stat_name == "total_probability":
                stat.stat_value += get_probability(str(pick_data['odds']))
            stat.save()
        return True
    else:
        for stat in stat_query:
            if stat.stat_name == "total_picks_placed":
                stat.stat_value += 1
            if stat.stat_name == "total_units_lost":
                stat.stat_value += int(pick_data['bet_amount'])
            if stat.stat_name == "number_of_failed_picks":
                stat.stat_value += 1
            if stat.stat_name == "total_probability":
                stat.stat_value += float(get_probability(str(pick_data['odds'])))
            stat.save()
        return False

            

def result_based_of_game_win(pick_data,event_result):
    seller_selected_outcome = pick_data['target_winner']
    actual_outcome = event_result['game_winner']
    return seller_selected_outcome == actual_outcome
    
    
    
    
def update_seller_stats_pointspread(seller,pick_data,result_data):
    pass
def update_buyer_stats(buyers):
    pass
