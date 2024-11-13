"""Sports api service manager that based of a specific pick is able to determine if the game happened
https://serpapi.com/sports-results -> this API. 
Now we are pertaining only to team vs team h2h
"""
from datetime import datetime
from serpapi import GoogleSearch

def has_game_happened(meta_data, game_result_data=None):
    if not game_result_data:
        team_1 = meta_data['team_1']
        team_2 = meta_data['team_2']
        event_date = meta_data['event_time']
        q = team_1 + " vs " + team_2 + " " + event_date.strftime("%B %d")
        print(q)
        
        params = {
            "api_key": "da9ec7582c440b3cab4c7e18feeb7114e57895337bf4b3489a5de130f48a0aa9",
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
        

    

