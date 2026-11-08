import os
from dataclasses import dataclass
from datetime import timedelta

from common.geo import METERS_PER_MILE

# OSRM times are for cars. Trucks rarely beat this on US highways.
TRUCK_MAX_MPH = float(os.getenv('TRUCK_MAX_MPH', '65'))


@dataclass
class Checkpoint:
    lat: float
    lon: float
    mile: float
    eta: object  # datetime
    covers_mi: float = 0.0
    weather: object = None  # weather.Conditions, or None past the forecast
    risk: object = None  # risk.Assessment, or None without weather


def truck_seconds(route):
    max_mps = TRUCK_MAX_MPH * METERS_PER_MILE / 3600
    return [max(seconds, meters / max_mps) for meters, seconds in zip(route.segment_m, route.segment_s, strict=True)]


def place_checkpoints(route, interval_mi, departure):
    """Checkpoint at the start, every `interval_mi` along the road, and at the destination."""
    seconds = truck_seconds(route)
    step_m = interval_mi * METERS_PER_MILE
    total_m = sum(route.segment_m)

    checkpoints = [_checkpoint(route.coords[0], 0, 0, departure)]
    next_m = step_m
    done_m = done_s = 0.0

    for i, (seg_m, seg_s) in enumerate(zip(route.segment_m, seconds, strict=True)):
        # The 1 m margin keeps float drift from adding a checkpoint right on top of the destination.
        while seg_m > 0 and next_m <= done_m + seg_m and next_m < total_m - 1:
            t = (next_m - done_m) / seg_m
            (lat1, lon1), (lat2, lon2) = route.coords[i], route.coords[i + 1]
            point = (lat1 + (lat2 - lat1) * t, lon1 + (lon2 - lon1) * t)
            checkpoints.append(_checkpoint(point, next_m, done_s + seg_s * t, departure))
            next_m += step_m
        done_m += seg_m
        done_s += seg_s

    checkpoints.append(_checkpoint(route.coords[-1], total_m, done_s, departure))
    _assign_coverage(checkpoints)
    return checkpoints


def _checkpoint(point, meters, seconds, departure):
    return Checkpoint(point[0], point[1], meters / METERS_PER_MILE, departure + timedelta(seconds=round(seconds)))


def _assign_coverage(checkpoints):
    # Each checkpoint stands for the road halfway to its neighbours, so coverage adds up to the trip.
    for i, cp in enumerate(checkpoints):
        before = cp.mile - checkpoints[i - 1].mile if i > 0 else 0
        after = checkpoints[i + 1].mile - cp.mile if i < len(checkpoints) - 1 else 0
        cp.covers_mi = (before + after) / 2
