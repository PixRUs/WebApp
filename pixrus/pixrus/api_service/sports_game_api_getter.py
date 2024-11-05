"""Sports api service manager that based of a specific pick is able to determine if the game happened
https://serpapi.com/sports-results -> this API. 
Now we are pertaining only to team vs team h2h
"""
from datetime import datetime
from serpapi import GoogleSearch 
def has_game_happened(meta_data, game_result_data = None):

    if not game_result_data:
        team_1 = meta_data['team_1']
        team_2 = meta_data['team_2']
        event_date = meta_data['event_time']
        q = team_1 + " vs " + team_2 + " " + event_date.strftime("%B %d")
        
        params = {
        "q":q,
        "location": "austin, texas, united states",
        "api_key": "_"
        }

        search = GoogleSearch(params)
        game_result_data = search.get_dict()['sports_results']
    is_final = 'status' in game_result_data['game_spotlight'] and game_result_data['game_spotlight']['status'].lower() == 'final'
    return is_final,game_result_data

def score_result(game_query_data,game_result_data = None):
    if not game_result_data:
        has_happened,game_result_data = has_game_happened(game_query_data)
        if not has_happened:
            return {}
        
    teams = game_result_data["game_spotlight"]["teams"]
    team1_score = int(teams[0]["score"]["T"])
    team2_score = int(teams[1]["score"]["T"])

    # Calculate score differentials
    differential_team1 = team1_score - team2_score
    differential_team2 = team2_score - team1_score

    # Create output
    output = [
        {
            "team": teams[0]["name"],
            "differential": differential_team1
        },
        {
            "team": teams[1]["name"],
            "differential": differential_team2
        }
    ]
    return output
        
    
meta_data_game_has_happened1 = {
    "bet_type": "h2h",
    "team_1": "Portland Trailblazers",
    "team_2": "New Orleans Pelicans",
    "event_time": datetime(2024, 11, 4)
}
meta_data_game_has_not_happened = {
    "bet_type": "h2h",
    "team_1": "Los Angeles Lakers",
    "team_2": "Dallas Mavericks",
    "event_time": datetime(2025, 1, 7)
}
meta_data_game_has_happened2 = {
    "bet_type": "h2h",
    "team_1": "Los Angeles Lakers",
    "team_2": "Sacramento Kings",
    "event_time": datetime(2024, 10, 26)
} 

    
    
print("GAME DIFFERENTIAL FOR GAMES THAT HAVE HAPPENED ")
print(score_result(meta_data_game_has_happened1))
print(score_result(meta_data_game_has_happened2))
print("GAME DIFFERENTIAL FOR GAMES THAT HAVE NOT HAPPEND")
print(score_result(meta_data_game_has_not_happened))

