import hashlib
import os
from dataclasses import dataclass

from django.core.cache import cache

from common.http import ProviderError, get_json

PHOTON_URL = os.getenv('PHOTON_URL', 'https://photon.komoot.io/api/')
FALLBACK_URL = os.getenv('GEOCODE_FALLBACK_URL', 'https://geocoding-api.open-meteo.com/v1/search')

# Photon refuses some cloud IP ranges. After a failure, go straight to the fallback for a while.
PHOTON_DOWN_KEY = 'geocode:photon-down'
PHOTON_DOWN_S = 5 * 60
PHOTON_TIMEOUT_S = 4

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


def _label(*parts):
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

    places = None
    if not cache.get(PHOTON_DOWN_KEY):
        try:
            places = _photon(query, limit)
        except ProviderError:
            cache.set(PHOTON_DOWN_KEY, True, PHOTON_DOWN_S)
    if places is None:
        places = _open_meteo(query, limit)

    cache.set(key, places, 24 * 60 * 60)
    return places


def resolve(query):
    places = search(query, limit=1)
    if not places:
        raise PlaceNotFound(f'No place called "{query}" in {SERVICE_AREA_NAME}.')
    return places[0]


def _photon(query, limit):
    south, west, north, east = SERVICE_AREA
    data = get_json(
        PHOTON_URL,
        {'q': query, 'limit': limit + 3, 'lang': 'en', 'bbox': f'{west},{south},{east},{north}'},
        retries=0,
        timeout=PHOTON_TIMEOUT_S,
    )
    places = {}
    for feature in data.get('features', []):
        lon, lat = feature['geometry']['coordinates']
        props = feature.get('properties', {})
        label = _label(props.get('name'), props.get('city'), props.get('state'), props.get('countrycode'))
        places.setdefault(label, Place(label, lat, lon))
    return list(places.values())[:limit]


def _open_meteo(query, limit):
    # Name search only, so "Austin, TX" searches "Austin" and ranks results that mention "TX" first.
    name, *hints = [part.strip().lower() for part in query.split(',')]
    data = get_json(FALLBACK_URL, {'name': name, 'count': 20, 'language': 'en', 'format': 'json'}, retries=1)

    places = {}
    for item in data.get('results') or []:
        label = _label(item.get('name'), item.get('admin1'), item.get('country_code'))
        place = Place(label, item['latitude'], item['longitude'])
        if in_service_area(place):
            places.setdefault(label, place)

    def matches(place):
        words = place.label.lower()
        return sum(hint in words for hint in hints if hint)

    return sorted(places.values(), key=matches, reverse=True)[:limit]
