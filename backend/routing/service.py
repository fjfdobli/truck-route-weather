import hashlib
from concurrent.futures import ThreadPoolExecutor

from django.core.cache import cache

from common.geo import Point, haversine_m, shift
from common.http import ProviderError

from . import osrm

ROUTE_COUNT = 3
MAX_OVERLAP = 0.8
MAX_DETOUR = 2.5
# Side offsets for detour waypoints, as a share of the straight-line trip length.
DETOUR_OFFSETS = (0.08, -0.08, 0.15, -0.15, 0.3, -0.3, 0.45, -0.45)


def find_routes(origin, destination):
    key = (
        'routes:'
        + hashlib.md5(
            f'{origin.lat:.5f},{origin.lon:.5f}|{destination.lat:.5f},{destination.lon:.5f}'.encode()
        ).hexdigest()
    )
    cached = cache.get(key)
    if cached is not None:
        return cached

    picked = []
    _take_distinct(osrm.fetch_routes([origin, destination], alternatives=True), picked)
    if len(picked) < ROUTE_COUNT:
        fastest = min(route.duration_s for route, _ in picked)
        detours = [r for r in _detours(origin, destination) if r.duration_s <= fastest * MAX_DETOUR]
        _take_distinct(sorted(detours, key=lambda r: r.duration_s), picked)

    routes = [route for route, _ in picked]
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


def _detours(origin, destination):
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = pool.map(lambda share: _route_via(origin, destination, share), DETOUR_OFFSETS)
        return [route for route in results if route]


def _route_via(origin, destination, share):
    trip_m = haversine_m(origin, destination)
    mid = Point((origin.lat + destination.lat) / 2, (origin.lon + destination.lon) / 2)

    # Unit vector of the trip in metres (north, east); the waypoint goes off to its side.
    north = haversine_m(origin, Point(destination.lat, origin.lon)) * (1 if destination.lat > origin.lat else -1)
    east = haversine_m(origin, Point(origin.lat, destination.lon)) * (1 if destination.lon > origin.lon else -1)
    length = (north**2 + east**2) ** 0.5 or 1
    via = shift(mid, -east / length * trip_m * share, north / length * trip_m * share)

    try:
        return osrm.fetch_routes([origin, via, destination])[0]
    except ProviderError:
        return None
