import json
import os
from collections import Counter

from common.geo import Point, haversine_m
from common.http import ProviderError, get_json

from .models import NO_ROUTE, TOO_FAR_FROM_ROAD, NoRouteError, Route, road_name, road_ref

VALHALLA_URL = os.getenv('VALHALLA_URL', 'https://valhalla1.openstreetmap.de')

KG_PER_LB = 0.45359237
NO_ROUTE_CODES = {442: NO_ROUTE, 443: NO_ROUTE, 170: TOO_FAR_FROM_ROAD, 171: TOO_FAR_FROM_ROAD}


def fetch_routes(points, weight_lb, alternatives=False):
    """Truck routes; the router avoids roads with weight limits below the load."""
    request = {
        'locations': [
            {'lat': p.lat, 'lon': p.lon, 'type': 'through' if 0 < i < len(points) - 1 else 'break'}
            for i, p in enumerate(points)
        ],
        'costing': 'truck',
        'costing_options': {'truck': {'weight': round(weight_lb * KG_PER_LB / 1000, 2)}} if weight_lb else {},
        'directions_type': 'maneuvers',
        'units': 'kilometers',
    }
    if alternatives:
        request['alternates'] = 2

    try:
        # Compact JSON: Valhalla rejects the '+' that a space becomes in a query string.
        data = get_json(f'{VALHALLA_URL}/route', {'json': json.dumps(request, separators=(',', ':'))}, retries=1)
    except ProviderError as exc:
        code = exc.payload.get('error_code') if isinstance(exc.payload, dict) else None
        if code in NO_ROUTE_CODES:
            raise NoRouteError(NO_ROUTE_CODES[code]) from exc
        raise

    trips = [data['trip']] + [alt['trip'] for alt in data.get('alternates', [])]
    return [_parse(trip, points[1:-1]) for trip in trips]


def _parse(trip, via):
    coords, segment_s = [], []
    road_m = Counter()
    for leg in trip['legs']:
        shape = decode(leg['shape'])
        offset = len(coords) - 1 if coords else 0
        coords += shape[1:] if coords else shape
        segment_s += [0.0] * (len(shape) - 1)

        for step in leg['maneuvers']:
            first, last = offset + step['begin_shape_index'], offset + step['end_shape_index']
            _spread(step['time'], coords, segment_s, first, last)
            ref = next((r for r in map(road_ref, step.get('street_names', [])) if r), None)
            if ref:
                road_m[ref] += step['length']

    segment_m = [haversine_m(Point(*a), Point(*b)) for a, b in zip(coords, coords[1:], strict=False)]
    via = [Point(p.lat, p.lon) for p in via]
    return Route(coords, segment_m, segment_s, road_name(road_m), via, 'truck', dict(road_m))


def _spread(seconds, coords, segment_s, first, last):
    """A maneuver's drive time, shared over its segments by length."""
    lengths = [haversine_m(Point(*coords[i]), Point(*coords[i + 1])) for i in range(first, last)]
    total = sum(lengths)
    for i, length in zip(range(first, last), lengths, strict=True):
        segment_s[i] = seconds * (length / total if total else 1 / len(lengths))


def decode(encoded, precision=6):
    """Google's polyline format at Valhalla's 6-digit precision."""
    coords, index, lat, lon = [], 0, 0, 0
    factor = 10**precision
    while index < len(encoded):
        for axis in range(2):
            shift = result = 0
            while True:
                byte = ord(encoded[index]) - 63
                index += 1
                result |= (byte & 0x1F) << shift
                shift += 5
                if byte < 0x20:
                    break
            delta = ~(result >> 1) if result & 1 else result >> 1
            if axis == 0:
                lat += delta
            else:
                lon += delta
        coords.append((lat / factor, lon / factor))
    return coords
