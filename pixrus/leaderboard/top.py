from seller.models import Stat
from seller.models import StatName,StatTimeUnits
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

def get_top_sellers(time_unit: StatTimeUnits,stat_name: StatName,n,riskiest = None):
    if stat_name == "total_probability":
        risk_list: List[Dist] = []
        total_probability = Stat.objects.filter(time_period=time_unit,stat_name=stat_name)
        for stat in total_probability:
            seller = stat.seller
            total = Stat.objects.get(time_period=time_unit,stat_name="total_picks_placed",seller=seller).stat_value
            risk_list.append(Dist(total,total_probability,seller))
            n = min(n,len(risk_list))
        if riskiest is True:
            risk_list.sort(reverse=True)
            tmp = []
            for _ in range(n):
                tmp.append(risk_list.pop().seller)
            return tmp
        else:
            risk_list.sort(reverse=False)
            tmp = []
            for _ in range(n):
                tmp.append(risk_list.pop().seller)
            return tmp

    top_unit_winners_queries = Stat.objects.filter(time_period=time_unit,stat_name=stat_name).order_by("-stat_value")[:n]
    tmp = []
    for query in top_unit_winners_queries:
        tmp.append(query.seller)
    return tmp
