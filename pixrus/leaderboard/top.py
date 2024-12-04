from seller.models import Stat
from pixrus.settings import ALLOWED_TIME_UNITS_FOR_LEADERBOARD,STAT_NAMES
from typing import List


class Dist:
    def __init__(self, total, prob, seller):
        self.total = total
        self.prob = prob
        self.seller = seller
        self.risk = self.calculate_risk()

    def calculate_risk(self):
        if self.total == 0:
            return 0
        return self.prob / self.total

    def __lt__(self, other):
        return self.risk < other.risk

def get_top_sellers(time_unit: ALLOWED_TIME_UNITS_FOR_LEADERBOARD,stat_name: STAT_NAMES,n,riskiest = None):
    if stat_name == "total_probability":
        riskiest: List[Dist] = []
        total_probability = Stat.objects.filter(time_unit=time_unit,stat_name=stat_name)
        for stat in total_probability:
            seller = stat.seller
            total = Stat.objects.get(time_unit=time_unit,stat_name="total_picks_placed",seller=seller)
            riskiest.append(Dist(total,total_probability,seller))
        if riskiest is True:
            return riskiest.sort(reverse=True)[:n]
        else:
            return riskiest.sort(reverse=False)[:n]


    top_unit_winners_queries = Stat.objects.filter(time_unit=time_unit,stat_name=stat_name).order_by("-total_units_won")[:n]
    return top_unit_winners_queries
