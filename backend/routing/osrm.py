import os
from collections import Counter
from dataclasses import dataclass, field

from common.geo import Point
from common.http import ProviderError, get_json

OSRM_URL = os.getenv('OSRM_URL', 'https://router.project-osrm.org')


@dataclass
class Route:
    coords: list  # [(lat, lon), ...]
    segment_m: list  # distance between coords[i] and coords[i + 1]
    segment_s: list  # driving time for the same segment
    name: str = ''
    via: list = field(default_factory=list)

    @property
    def distance_m(self):
        return sum(self.segment_m)

    @property
    def duration_s(self):
        return sum(self.segment_s)


class NoRouteError(ProviderError):
    """The places are fine, but no road connects them. The user can fix this, so it is not a server fault."""


NO_ROUTE_MESSAGES = {
    'NoRoute': 'No road connects these two places. Pick a start and an end on the same road network.',
    'NoSegment': 'One of the places is too far from a road. Try a nearby town or address.',
}


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
        raise NoRouteError(NO_ROUTE_MESSAGES.get(data.get('code'), NO_ROUTE_MESSAGES['NoRoute']))

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

    # Name a route after the highways it spends the most distance on.
    main_roads = [ref for ref, _ in road_m.most_common(2)]
    return Route(coords, segment_m, segment_s, ' / '.join(main_roads), [Point(p.lat, p.lon) for p in via])
