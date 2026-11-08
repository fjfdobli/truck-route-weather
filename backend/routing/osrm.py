import os
from collections import Counter

from common.geo import Point
from common.http import ProviderError, get_json

from .models import NO_ROUTE, TOO_FAR_FROM_ROAD, NoRouteError, Route, road_name

OSRM_URL = os.getenv('OSRM_URL', 'https://router.project-osrm.org')

NO_ROUTE_MESSAGES = {'NoRoute': NO_ROUTE, 'NoSegment': TOO_FAR_FROM_ROAD}


def fetch_routes(points, alternatives=False):
    path = ';'.join(f'{p.lon:.6f},{p.lat:.6f}' for p in points)
    try:
        data = get_json(
            f'{OSRM_URL}/route/v1/driving/{path}',
            {
                'alternatives': 3 if alternatives else 'false',
                'overview': 'full',
                'geometries': 'geojson',
                'annotations': 'distance,duration',
                'steps': 'true',
                'continue_straight': 'true',
            },
        )
    except ProviderError as exc:
        code = exc.payload.get('code') if isinstance(exc.payload, dict) else None
        if code in NO_ROUTE_MESSAGES:
            raise NoRouteError(NO_ROUTE_MESSAGES[code]) from exc
        raise

    if data.get('code') != 'Ok':
        raise NoRouteError(NO_ROUTE_MESSAGES.get(data.get('code'), NO_ROUTE))

    return [_parse(raw, points[1:-1]) for raw in data['routes']]


def _parse(raw, via):
    coords = [(lat, lon) for lon, lat in raw['geometry']['coordinates']]
    segment_m, segment_s = [], []
    road_m = Counter()
    for leg in raw['legs']:
        segment_m += leg['annotation']['distance']
        segment_s += leg['annotation']['duration']
        for step in leg.get('steps', []):
            ref = step.get('ref', '').split(';')[0].strip()
            if ref:
                road_m[ref] += step['distance']

    if len(segment_m) != len(coords) - 1:
        raise ProviderError('Routing response geometry and annotations do not line up')

    return Route(
        coords, segment_m, segment_s, road_name(road_m), [Point(p.lat, p.lon) for p in via], roads=dict(road_m)
    )
