from dataclasses import dataclass

import risk
import routing
import weather

from .checkpoints import place_checkpoints
from .recommend import explain, summarize, warning


@dataclass
class RoutePlan:
    route: object
    checkpoints: list
    summary: object = None

    @property
    def arrival(self):
        return self.checkpoints[-1].eta


@dataclass
class TripPlan:
    routes: list  # RoutePlan, in the order the router returned them
    ranking: list  # route indexes
    reason: str
    warning: object

    @property
    def recommended(self):
        return self.ranking[0]


def plan_trip(origin, destination, departure, weight_lb, interval_mi):
    plans = [
        RoutePlan(route, place_checkpoints(route, interval_mi, departure))
        for route in routing.find_routes(origin, destination)
    ]

    # One batched weather lookup for every checkpoint on every route.
    checkpoints = [cp for plan in plans for cp in plan.checkpoints]
    series = weather.load(weather.snap(cp.lat, cp.lon) for cp in checkpoints)
    for cp in checkpoints:
        cp.weather = series[weather.snap(cp.lat, cp.lon)].at(cp.eta)
        cp.risk = risk.assess(cp.weather, weight_lb)

    for plan in plans:
        hours = (plan.arrival - departure).total_seconds() / 3600
        plan.summary = summarize(plan.checkpoints, hours)

    ranking = sorted(range(len(plans)), key=lambda i: plans[i].summary.sort_key())
    best = plans[ranking[0]].summary
    runner_up = plans[ranking[1]].summary if len(ranking) > 1 else None

    return TripPlan(plans, ranking, explain(best, runner_up), warning([p.summary for p in plans]))
