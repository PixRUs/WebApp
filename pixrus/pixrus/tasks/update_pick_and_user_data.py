import os
import sys
import django
from pathlib import Path

# Get the root of the project dynamically
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pixrus.settings')
django.setup()

from datetime import datetime
from product.models import ActivePick
from util import update_buyer_and_seller_stats
from game_results_getter import get_score_result


all_active_picks = ActivePick.objects.all()
for active_pick in all_active_picks: 
    if active_pick.game_data is None:
        continue
    event_start = active_pick.event_start
    type_of_pick = active_pick.type_of_pick
    game_query_data = {}
    if type_of_pick == "moneyline":
        if event_start is None or event_start.date() <= datetime.today().date():
            game_data =  active_pick.game_data
            team_1 = game_data.get('team_1')
            team_2 = game_data.get('team_2')
            if not team_1 or not team_2 or not event_start:
                continue
            game_query_data = {
                "team_1": team_1,
                "team_2": team_2,
                "event_time": event_start
            }
    has_happened,result = get_score_result(game_query_data, type_of_pick)
    if has_happened:
        seller = active_pick.seller
        buyers = active_pick.buyers_with_access
        pick_data = active_pick.pick_data
        pick_success = update_buyer_and_seller_stats(seller=seller,buyers=buyers,pick_data=pick_data,result_data=result,type_of_pick=type_of_pick)
        seller.save()
        pick_data['pick_success'] = pick_success
        ActivePick.make_historical(active_pick,event_result=result,pick_data=pick_data)


        
