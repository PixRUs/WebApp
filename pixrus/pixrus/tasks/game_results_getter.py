"""Sports api service manager that based of a specific pick is able to determine if the game happened
https://serpapi.com/sports-results -> this API. 
Now we are pertaining only to team vs team h2h
"""
from datetime import datetime
from serpapi import GoogleSearch
import os
VENDOR_API_KEY = os.getenv('SERPAPI_ID')

def has_game_happened_moneyline(query_data):
    is_final = True
    team_1 = query_data.get('team_1')
    team_2 = query_data.get('team_2')
    event_date_str = query_data.get('event_time')
    if not team_1 or not team_2 or not event_date_str:
        return False,{}

    event_date_str = str(event_date_str)
    event_date = datetime.fromisoformat(event_date_str)
    q = f"{team_1} vs {team_2} {event_date.strftime('%B %d')}"
    
    params = {
        "api_key": VENDOR_API_KEY,
        "engine": "google",
        "q": q,
        "location": "Austin, Texas, United States",
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en"
    }

    search = GoogleSearch(params)
    search_results = search.get_dict()
    is_final = False
    game_result_data = {}

    if 'sports_results' in search_results: 
        game_result_data = search_results['sports_results']
        is_final = 'status' in game_result_data['game_spotlight'] and game_result_data['game_spotlight']['status'].lower() == 'final'
        
    elif 'search_information' in search_results and 'spelling_fix' in search_results['search_information']:
        # Retry with corrected spelling
        corrected_query = search_results['search_information']['spelling_fix']
        params["q"] = corrected_query
        search = GoogleSearch(params)
        search_results = search.get_dict()
        if 'sports_results' in search_results: 
            game_result_data = search_results['sports_results']
            is_final = 'status' in game_result_data['game_spotlight'] and game_result_data['game_spotlight']['status'].lower() == 'final'
        else: 
            return False, {}
    return is_final, game_result_data


def get_score_result(game_query_data,type_of_pick):
    bet_type_functions = {
        "h2h": score_result_moneyline,
    }
    bet_type_function = bet_type_functions.get(type_of_pick)
    if bet_type_function:
        return bet_type_function(game_query_data)

def score_result_moneyline(game_query_data):
    has_happened,game_result_data = has_game_happened_moneyline(game_query_data)
    if not has_happened or game_result_data is None:
        return False,{}

    teams = game_result_data["game_spotlight"]["teams"] 
    team1_score = int(teams[0]["score"]["T"])
    team2_score = int(teams[1]["score"]["T"])

    differential_team1 = team1_score - team2_score
    differential_team2 = team2_score - team1_score
    if team2_score > team1_score:
        team_winner = teams[1]['name']
    elif team1_score > team2_score:
        team_winner = teams[0]['name']
    else: 
        team_winner = "Draw"
    
    return True,{
        "team_1": teams[0]['name'],
        "team_2": teams[1]['name'],
        "team_1_points": team1_score,
        "team_2_points": team2_score,
        "team_1_differential": differential_team1,
        "team_2_differential": differential_team2,
        "game_winner":team_winner,
    }

        

    

