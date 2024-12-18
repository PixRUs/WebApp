from typing import List
from django.db.models import Sum,Count,Avg

from product.models import HistoricalPick
from datetime import datetime, timedelta

from seller.models import Seller


def get_top_sellers(time_delta,num_sellers):
    if time_delta == 0:
        return get_top(HistoricalPick.objects.all(), num_sellers)
    delta = datetime.now() - timedelta(days=time_delta)
    historical_pick_queries = HistoricalPick.objects.filter(posted_at__gte=delta)
    return get_top(historical_pick_queries,num_sellers)

def get_top(historical_pick_queries,num_sellers):

    sellers_with_most_number_of_units_made = [
        (Seller.objects.get(id=seller['seller']), seller['total_units'])
        for seller in (
            historical_pick_queries
            .values('seller')
            .annotate(total_units=Sum('units_won'))
            .order_by('-total_units')[:num_sellers]
        )
    ]

    sellers_with_most_number_of_successful_bets = [
        (Seller.objects.get(id=seller['seller']), seller['successful_bets'])
        for seller in (
            historical_pick_queries
            .values('seller')
            .annotate(successful_bets=Count('id'))
            .order_by('-successful_bets')[:num_sellers]
        )
    ]

    safest_sellers = [
        (Seller.objects.get(id=seller['seller']), round(seller['average_probability'], 2))
        for seller in (
            historical_pick_queries
            .values('seller')
            .annotate(average_probability=Avg('probability'))
            .order_by('-average_probability')[:num_sellers]
        )
    ]

    riskiest_sellers = [
        (Seller.objects.get(id=seller['seller']), round(seller['average_probability'], 2))
        for seller in (
            historical_pick_queries
            .values('seller')
            .annotate(average_probability=Avg('probability'))
            .order_by('average_probability')[:num_sellers]
        )
    ]

    return {
        "sellers_with_most_number_of_units_made": sellers_with_most_number_of_units_made,
        "sellers_with_most_number_of_successful_bets": sellers_with_most_number_of_successful_bets,
        "riskiest_sellers": riskiest_sellers,
        "safest_sellers": safest_sellers,
    }
