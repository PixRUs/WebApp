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


def get_upcoming_odds(sport_league,markets, regions='us', odds_format='american',date_format=''):
    url = f"{BASE_URL}/{sport_league}/odds"
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

def get_odds(sport_league,type_of_pick,verbal_type_of_pick):
    response_data = {}
    request_object = ApiRequest.get_request_data(sport_league=sport_league, type_of_pick=type_of_pick)
    if request_object is None or request_object.response_data == {}:
        response_data = get_upcoming_odds(sport_league=sport_league,markets=type_of_pick)
    else:
        return request_object

    obj,created = ApiRequest.objects.get_or_create(
        sport_league=sport_league,
        type_of_pick=type_of_pick,
        defaults={
            'endpoint': BASE_URL,
            'sport_league': sport_league,
            'type_of_pick': type_of_pick,
            'response_data': response_data,
            'type_of_pick_verbal': verbal_type_of_pick
        }
    )
    if not created:
        obj.response_data = response_data
        obj.request_time = datetime.now(ZoneInfo("US/Eastern"))
        obj.save()


    return obj


