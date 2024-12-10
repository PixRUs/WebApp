""" For now current stats is storing  number of successful picks, and number of unsuccesful picks. 
    Each time we just update the sellers. Need the implementation to be such that I wont have to change the whole structure if I were to add another statistic / sport.
"""

def did_game_hit(pick_data,result_data,type_of_pick):
    """_summary_

    Args:
        result_data (json): should list the game winner, teams invloved. 
        pick_data (_type_): should list the pick who the 

    """
    bet_type_functions = {
        "h2h": h2h_game_hit,
        "pointspread": pointspread_game_hit,
    }
    bet_type_function = bet_type_functions.get(type_of_pick)
    if bet_type_function:
        return bet_type_function(pick_data,result_data)
    return False


def h2h_game_hit(pick_data,event_result):
    seller_selected_outcome = pick_data['target_winner']
    actual_outcome = event_result['game_winner']
    return seller_selected_outcome == actual_outcome

def pointspread_game_hit(pick_data,event_result):
    pass