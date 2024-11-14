import os
import sys
import django
from pathlib import Path
import datetime

# Get the root of the project dynamically
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pixrus.settings')
django.setup()


from product.models import ActivePick, HistoricalPick
from pixrus.api_services.game_results_getter import score_result

all_active_picks = ActivePick.objects.all()
for active_pick in all_active_picks: 
    if active_pick.event_data is None:
        continue
    event_data =  active_pick.event_data
    if not event_data:
        continue
    team_1 = event_data.get('team_1')
    team_2 = event_data.get('team_2')
    event_time = event_data.get('event_time')
    if not team_1 or not team_2 or not event_time:
        continue

    game_query_data = {
        "team_1": team_1,
        "team_2": team_2,
        "event_time": event_time  

    }
    has_happened,result = score_result(game_query_data=game_query_data)
    if has_happened:
        ActivePick.make_historical(active_pick,result)
