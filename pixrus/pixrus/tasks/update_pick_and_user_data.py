import os
import sys
import django
from pathlib import Path
from django.utils.timezone import now
import pytz
# Get the root of the project dynamically
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pixrus.settings')

# Initialize Django
django.setup()

from datetime import datetime
from product.models import ActivePick
from pixrus.tasks.utils.game_results_getter import get_score_result

all_active_picks = ActivePick.objects.all()
for active_pick in all_active_picks: 
    if active_pick.game_data is None:
        continue
    event_start = active_pick.event_start
    type_of_pick = active_pick.type_of_pick
    game_query_data = {}
    if type_of_pick == "h2h":
        if event_start is None or event_start.date() <= now().date():
            game_data =  active_pick.game_data
            home_team = game_data.get('home_team')
            away_team = game_data.get('away_team')
            if not home_team or not away_team or not event_start:
                continue
            game_query_data = {
                "team_1": home_team,
                "team_2": away_team,
                "event_time": event_start
            }
    has_happened,result = get_score_result(game_query_data, type_of_pick)
    if has_happened:
        seller = active_pick.seller
        buyers = active_pick.buyers_with_access
        pick_data = active_pick.pick_data
        ActivePick.make_historical(active_pick, event_result=result, pick_data=pick_data)




        
