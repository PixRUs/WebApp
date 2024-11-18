""" For now current stats is storing  number of successful picks, and number of unsuccesful picks. 
    Each time we just update the sellers. Need the implementation to be such that I wont have to change the whole structure if I were to add another statistic / sport.
"""


def update_buyer_and_seller_stats(pick_data,result_data,seller,buyers):
    """_summary_

    Args:
        result_data (json): should list the game winner, teams invloved. 
        pick_data (_type_): should list the pick who the 
        seller (_type_): seller associated with the pick. 
        buyers (_type_): buyers who have purchase the pick. 
    """
    type_of_bet = pick_data['type']
    bet_type_functions = {
        "moneyline": update_seller_stats_moneyline,
        "pointspread": update_seller_stats_pointspread,
    }
    bet_type_function = bet_type_functions.get(type_of_bet)
    if bet_type_function:
        bet_type_function(seller, pick_data=pick_data, result_data=result_data)
    


def update_seller_stats_moneyline(seller,pick_data,result_data):
    #Moneyline: Betting on the team or player to win the game outright, regardless of the score.
    seller_stats = seller.stats
    if(result_based_of_game_win(pick_data=pick_data,result_data=result_data)):
        seller_stats['num_of_success'] += 1
    else:
        seller_stats['num_of_failures'] += 1

            

def result_based_of_game_win(pick_data,result_data):
    seller_selected_outcome = pick_data['seller_pick']['target']
    actual_outcome = result_data['winner']
    return seller_selected_outcome == actual_outcome
    
    
    
    
def update_seller_stats_pointspread(seller,pick_data,result_data):
    pass
def update_buyer_stats(buyers):
    pass
