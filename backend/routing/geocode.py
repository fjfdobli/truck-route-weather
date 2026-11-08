import hashlib
import os
from dataclasses import dataclass

from django.core.cache import cache

from common.http import get_json

PHOTON_URL = os.getenv('PHOTON_URL', 'https://photon.komoot.io/api/')

# One connected road network: the US, Canada and Mexico. (south, west, north, east)
SERVICE_AREA = (14.0, -170.0, 72.0, -52.0)
SERVICE_AREA_NAME = 'the US, Canada and Mexico'


class PlaceNotFound(Exception):
    pass


@dataclass(frozen=True)
class Place:
    label: str
    lat: float
    lon: float


def in_service_area(place):
    south, west, north, east = SERVICE_AREA
    return south <= place.lat <= north and west <= place.lon <= east


def _label(props):
    parts = [props.get('name'), props.get('city'), props.get('state'), props.get('countrycode')]
    seen = []
    for part in parts:
        if part and part not in seen:
            seen.append(part)
    return ', '.join(seen)


def search(query, limit=5):
    query = query.strip()
    if len(query) < 2:
        return []

    key = 'geocode:' + hashlib.md5(f'{query.lower()}|{limit}'.encode()).hexdigest()
    cached = cache.get(key)
    if cached is not None:
        return cached

    south, west, north, east = SERVICE_AREA
    data = get_json(
        PHOTON_URL,
        {
            'q': query,
            'limit': limit + 3,
            'lang': 'en',
            'bbox': f'{west},{south},{east},{north}',
        },
    )
    places = {}
    for feature in data.get('features', []):
        lon, lat = feature['geometry']['coordinates']
        label = _label(feature.get('properties', {}))
        places.setdefault(label, Place(label, lat, lon))
    places = list(places.values())[:limit]

    cache.set(key, places, 24 * 60 * 60)
    return places


def resolve(query):
    places = search(query, limit=1)
    if not places:
        raise PlaceNotFound(f'No place called "{query}" in {SERVICE_AREA_NAME}.')
    return places[0]
