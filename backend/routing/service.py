import hashlib
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from django.core.cache import cache

from common.geo import Point, haversine_m, shift
from common.http import ProviderError

from . import osrm, valhalla
from .models import NoRouteError, name_apart

ROUTE_COUNT = 3
MAX_OVERLAP = 0.8
MAX_DETOUR = 2.5
# Side offsets for detour waypoints, as a share of the straight-line trip length.
DETOUR_OFFSETS = (0.08, -0.08, 0.15, -0.15, 0.3, -0.3, 0.45, -0.45)
# Loads are routed in 1,000 lb steps so nearby weights share cached routes.
WEIGHT_STEP_LB = 1000


def find_routes(origin, destination, weight_lb=0):
    """Up to three distinct routes: truck routes when the truck router answers, car routes otherwise."""
    weight_lb = -(-weight_lb // WEIGHT_STEP_LB) * WEIGHT_STEP_LB
    key = (
        'routes:'
        + hashlib.md5(
            f'{origin.lat:.5f},{origin.lon:.5f}|{destination.lat:.5f},{destination.lon:.5f}|{weight_lb}'.encode()
        ).hexdigest()
    )
    cached = cache.get(key)
    if cached is not None:
        return cached

    route = partial(valhalla.fetch_routes, weight_lb=weight_lb)
    try:
        first = route([origin, destination], alternatives=True)
    except NoRouteError:
        raise
    except ProviderError:
        # Down, or the trip is longer than the public truck router allows.
        route = osrm.fetch_routes
        first = route([origin, destination], alternatives=True)

    picked = []
    _take_distinct(first, picked)
    if len(picked) < ROUTE_COUNT:
        fastest = min(r.duration_s for r, _ in picked)
        detours = [r for r in _detours(route, origin, destination) if r.duration_s <= fastest * MAX_DETOUR]
        _take_distinct(sorted(detours, key=lambda r: r.duration_s), picked)

    routes = [r for r, _ in picked]
    name_apart(routes)
    cache.set(key, routes)
    return routes


def _take_distinct(routes, picked):
    """Adds routes to `picked` as (route, cells) until it is full, skipping near-duplicates."""
    for route in routes:
        if len(picked) == ROUTE_COUNT:
            return
        cells = {(round(lat, 3), round(lon, 3)) for lat, lon in route.coords}
        if all(_overlap(cells, other) < MAX_OVERLAP for _, other in picked):
            picked.append((route, cells))


def _overlap(a, b):
    shared = len(a & b)
    return max(shared / len(a), shared / len(b))


def _detours(route, origin, destination):
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = pool.map(lambda share: _route_via(route, origin, destination, share), DETOUR_OFFSETS)
        return [r for r in results if r]


def _route_via(route, origin, destination, share):
    trip_m = haversine_m(origin, destination)
    mid = Point((origin.lat + destination.lat) / 2, (origin.lon + destination.lon) / 2)

    # Unit vector of the trip in metres (north, east); the waypoint goes off to its side.
    north = haversine_m(origin, Point(destination.lat, origin.lon)) * (1 if destination.lat > origin.lat else -1)
    east = haversine_m(origin, Point(origin.lat, destination.lon)) * (1 if destination.lon > origin.lon else -1)
    length = (north**2 + east**2) ** 0.5 or 1
    via = shift(mid, -east / length * trip_m * share, north / length * trip_m * share)

    try:
        return route([origin, via, destination])[0]
    except ProviderError:
        return None
