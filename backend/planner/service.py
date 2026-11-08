from dataclasses import dataclass

import risk
import routing
import weather

from .checkpoints import place_checkpoints
from .heatmap import Heatmap, corridor, fill
from .recommend import explain, summarize, warning

# Open-Meteo's free tier allows 600 locations a minute. Checkpoints use at most 200
# and the heatmap 100, so one plan costs about half a minute's budget.
MAX_CHECKPOINT_CELLS = 200
CHECKPOINT_CELL_SIZES = (0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0)


def checkpoint_grid(checkpoints):
    """The finest weather grid that keeps every checkpoint within the location budget."""
    for cell_deg in CHECKPOINT_CELL_SIZES:
        cells = {weather.snap(cp.lat, cp.lon, cell_deg) for cp in checkpoints}
        if len(cells) <= MAX_CHECKPOINT_CELLS:
            break
    return cell_deg


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
    heatmap: object

    @property
    def recommended(self):
        return self.ranking[0]


def plan_trip(origin, destination, departure, weight_lb, interval_mi):
    plans = [
        RoutePlan(route, place_checkpoints(route, interval_mi, departure))
        for route in routing.find_routes(origin, destination)
    ]

    cell_deg, heat_cells = corridor(plan.route for plan in plans)
    checkpoints = [cp for plan in plans for cp in plan.checkpoints]
    grid = checkpoint_grid(checkpoints)
    cell_of = {id(cp): weather.snap(cp.lat, cp.lon, grid) for cp in checkpoints}

    # One batched weather lookup for every checkpoint and every heatmap cell.
    series = weather.load(list(cell_of.values()) + heat_cells)
    for cp in checkpoints:
        cp.weather = series[cell_of[id(cp)]].at(cp.eta)
        cp.risk = risk.assess(cp.weather, weight_lb)

    for plan in plans:
        hours = (plan.arrival - departure).total_seconds() / 3600
        plan.summary = summarize(plan.checkpoints, hours)

    ranking = sorted(range(len(plans)), key=lambda i: plans[i].summary.sort_key())
    best = plans[ranking[0]].summary
    runner_up = plans[ranking[1]].summary if len(ranking) > 1 else None

    heatmap = fill(Heatmap(departure, cell_deg, heat_cells), series, weight_lb)
    return TripPlan(plans, ranking, explain(best, runner_up), warning([p.summary for p in plans]), heatmap)
