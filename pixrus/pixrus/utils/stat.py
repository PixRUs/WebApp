from datetime import datetime, timedelta
from product.models import HistoricalPick

def get_stats(seller,time_delta):
    if time_delta == 0:
        return calculate_with_q(HistoricalPick.objects.filter(seller=seller))

    delta = datetime.now() - timedelta(days=time_delta)
    historical_pick_queries = HistoricalPick.objects.filter(seller=seller,posted_at__gte=delta)
    return calculate_with_q(historical_pick_queries)

def calculate_with_q(historical_pick_queries):
    number_of_placed_picks = historical_pick_queries.count()
    units_won = 0
    number_of_successful_picks = 0
    total_probability = 0
    for hist in historical_pick_queries:
        units_won += hist.units_won
        total_probability += hist.probability
        if hist.did_seller_succeed:
            number_of_successful_picks += 1

    stats = {'number_of_placed_picks': number_of_placed_picks, 'units_won': units_won,
             'average_probability': total_probability / number_of_placed_picks if number_of_placed_picks > 0 else 0,
             'number_of_successful_picks': number_of_successful_picks}
    stats = [{'stat_verbal': key.replace('_', ' ').capitalize(), 'stat_value': value} for key, value in stats.items()]

    return stats