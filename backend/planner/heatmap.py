from dataclasses import dataclass
from datetime import timedelta

import risk
import weather
from common.geo import METERS_PER_MILE

HOURS = 48
SAMPLE_EVERY_MI = 15
MAX_CELLS = 100
CELL_SIZES = (0.3, 0.5, 1.0, 1.5, 2.0, 3.0)


@dataclass
class Heatmap:
    start: object  # datetime of hour 0
    cell_deg: float
    cells: list
    values: list = None


def corridor(routes):
    """Grid cells within one cell of every route, coarser for very long trips."""
    samples = [p for route in routes for p in _samples(route)]
    for cell_deg in CELL_SIZES:
        cells = _around(samples, cell_deg)
        if len(cells) <= MAX_CELLS:
            break
    return cell_deg, cells


def fill(heatmap, series, weight_lb):
    heatmap.values = []
    for hour in range(HOURS + 1):
        when = heatmap.start + timedelta(hours=hour)
        heatmap.values.append([risk.intensity(series[c].at(when), weight_lb) for c in heatmap.cells])
    return heatmap


def _samples(route):
    step = SAMPLE_EVERY_MI * METERS_PER_MILE
    travelled = step  # take the first point too
    for coord, seg_m in zip(route.coords, route.segment_m + [0], strict=True):
        if travelled >= step:
            yield coord
            travelled = 0
        travelled += seg_m
    yield route.coords[-1]


def _around(points, cell_deg):
    cells = {}
    for lat, lon in points:
        clat, clon = weather.snap(lat, lon, cell_deg)
        for dlat in (-cell_deg, 0, cell_deg):
            for dlon in (-cell_deg, 0, cell_deg):
                cells[(round(clat + dlat, 4), round(clon + dlon, 4))] = None
    return list(cells)
