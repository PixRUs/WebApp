from datetime import datetime
import pytz
import requests
from serpapi import GoogleSearch
from product.models import ApiRequest
import requests
import os

# api_key_SERP-API
SERP_KEY = 'a024009b966e529676d4497b8bb73928ca784ba41e9f66e21adeb13f28f6c3a7'
# api_key_ODDS-API
API_KEY = os.getenv('ODDS_ID')
BASE_URL = 'https://api.the-odds-api.com/v4/sports'


def get_upcoming_odds(sport,markets, regions='us', odds_format='american',date_format=''):
    url = f"{BASE_URL}/{sport}/odds"
    params = {
        'apiKey': API_KEY,
        'regions': regions,
        'oddsFormat': odds_format,
        'markets': markets,
        'dateFormat': date_format,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()  # odds data
    else:
        print(f"Error: {response.status_code} - {response.json()}")
        return None
from zoneinfo import ZoneInfo

def get_odds(sport,league,type_of_pick):
    response_data = {}
    if sport == 'basketball':
        if league == 'nba':
            if type_of_pick == 'h2h':
                request_object = ApiRequest.get_request_data(sport=sport,league=league, type_of_pick='h2h')
                if request_object is None or request_object.response_data == {}:
                    response_data = get_nba_odd_data_h2h()
                else:
                    return request_object

    obj,created = ApiRequest.objects.get_or_create(
        sport=sport,
        league=league,
        type_of_pick=type_of_pick,
        defaults={
            'endpoint': BASE_URL,
            'sport': sport,
            'league': league,
            'type_of_pick': type_of_pick,
            'response_data': response_data
        }
    )
    if not created:
        obj.response_data = response_data
        obj.request_time = datetime.now(ZoneInfo("US/Eastern"))
        obj.save()


    return obj

# testing section
def get_nba_odd_data_h2h():
    print("Making request..")
    odds_data = get_upcoming_odds(sport='basketball_nba', markets='h2h')
    odd_json = {"sport": "basketball", "league": "nba", "type": "h2h"}
    game_data = []
    if odds_data:
        for index, game in enumerate(odds_data):
            # Generate a unique ID for each game
            game_id = f"{game['home_team']}_vs_{game['away_team']}_{index}"

            game_entry = {
                "id": game_id,  # Add the unique ID
                "home_team": game['home_team'],
                "away_team": game['away_team'],
                "commence_time": format_time(game['commence_time']),
                "bookmakers": []
            }

            for bookmaker in game['bookmakers']:
                bookmaker_entry = {
                    "title": bookmaker['title'],
                    "markets": []
                }

                for market in bookmaker['markets']:
                    market_entry = {
                        "outcomes": []
                    }

                    for outcome in market['outcomes']:
                        outcome_entry = {
                            "name": outcome['name'],
                            "multiplier": outcome['price']
                        }
                        market_entry["outcomes"].append(outcome_entry)

                    bookmaker_entry["markets"].append(market_entry)

                game_entry["bookmakers"].append(bookmaker_entry)

            game_data.append(game_entry)
    odd_json['games'] = game_data
    return odd_json

def format_time(time):
    print(time)
    utc_time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=pytz.utc)

    # Convert to Eastern Time (ET)
    eastern = pytz.timezone("US/Eastern")
    et_time = utc_time.astimezone(eastern)
    return et_time.strftime("%Y-%m-%d %H:%M:%S %Z")

def get_available_sports():
    url = f"{BASE_URL}/"
    params = {'apiKey': API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()  # list of sports
    else:
        print(f"Error: {response.status_code} - {response.json()}")
        return None


def get_in_play_odds(sport='basketball_nba', regions='us'):
    url = f"{BASE_URL}/{sport}/odds"
    params = {
        'apiKey': API_KEY,
        'regions': regions,
        'markets': 'h2h',
        'oddsFormat': 'decimal',
        'dateFormat': 'iso',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return [game for game in response.json() if game['commence_time'] <= datetime.now().isoformat()]
    else:
        print(f"Error: {response.status_code} - {response.json()}")
        return None


def get_future_event_odds(sport='basketball_nba', regions='us', days_ahead=7):
    url = f"{BASE_URL}/{sport}/odds"
    future_date = (datetime.now() + timedelta(days=days_ahead)).isoformat()
    params = {
        'apiKey': API_KEY,
        'regions': regions,
        'markets': 'h2h',
        'oddsFormat': 'decimal',
        'dateFormat': 'iso',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return [game for game in response.json() if game['commence_time'] > future_date]
    else:
        print(f"Error: {response.status_code} - {response.json()}")
        return None


# def get_sportsOdds_data():
#     url = "https://api.the-odds-api.com/v4/sports/?apiKey=YOUR_API_KEY"  # Replace with your API endpoint
#     headers = {
#         "Authorization": "Bearer yourapikey"
#     }
#     response = requests.get(url, headers=headers)
#     return response.json() if response.status_code == 200 else None

def get_sportsResults_data():
    params = {
        "q": "Manchester United F.C.",
        "location": "austin, texas, united states",
        "api_key": SERP_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    sports_results = results["sports_results"]


def get_upcoming_nba_games():
    params = {
        "q": "NBA schedule",
        "location": "austin, texas, united states",
        "api_key": SERP_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if 'sports_results' in results:
        sports_results = results['sports_results']

        if 'games' in sports_results:
            games = sports_results['games']

            # extract the next x upcoming games
            upcoming_games = games[:6]

            # print the upcoming gamess
            for game in upcoming_games:
                teams = game.get('teams', [])
                if len(teams) == 2:
                    team1 = teams[0].get('name', 'Unknown Team 1')
                    team2 = teams[1].get('name', 'Unknown Team 2')
                    date = game.get('date', 'Unknown Date')
                    print(f"{team1} vs {team2} on {date}")
        else:
            print("No games information found in sports results.")
    else:
        print("No sports results found.")


# get_upcoming_nba_games()


def get_sport_schedule_UI():
    # List of supported sports and leagues for validation
    supported_sports = ["nba", "soccer", "tennis", "baseball"]
    soccer_leagues = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]

    # Ask the user for the sport they are interested in
    sport = input(
        "Enter the sport you want to see the schedule for (e.g., NBA, Soccer, Tennis, Baseball): ").strip().lower()

    # Check if the sport is supported
    if sport not in supported_sports:
        print("Sport not recognized or unsupported. Please check your input and try again.")
        return

    # Special handling for soccer, asking for a specific league
    if sport == "soccer":
        print("Available soccer leagues: Premier League, La Liga, Serie A, Bundesliga, Ligue 1")
        league = input("Please specify the league you want to see the schedule for: ").strip()

        # Validate if the league is one of the known options
        if league not in soccer_leagues:
            print("League not recognized. Please enter a valid league name.")
            return

        # Modify the search query to include the league name
        query = f"{league} schedule"
    else:
        # For other sports, set the query directly
        query = f"{sport.upper()} schedule"

    # Set up parameters for the search
    params = {
        "q": query,
        "location": "austin, texas, united states",
        "api_key": SERP_KEY
    }

    # Perform the search
    search = GoogleSearch(params)
    results = search.get_dict()

    # Check if 'sports_results' is in the results
    if 'sports_results' in results and 'games' in results['sports_results']:
        games = results['sports_results']['games']

        print(f"Total games found: {len(games)}")

        # Display the upcoming games
        print(f"\nUpcoming {query} for next 6 games:")
        for game in games[:6]:  # Limit to the next 8 games
            teams = game.get('teams', [])
            if len(teams) == 2:
                team1 = teams[0].get('name', 'Unknown Team 1')
                team2 = teams[1].get('name', 'Unknown Team 2')
                date = game.get('date', 'Unknown Date')
                print(f"{team1} vs {team2} on {date}")
    else:
        print("No games found for the specified sport or league.")

# get_sport_schedule_UI()
