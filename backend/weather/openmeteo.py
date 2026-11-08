import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime

from django.core.cache import cache

from common.http import ProviderError, get_json

OPEN_METEO_URL = os.getenv('OPEN_METEO_URL', 'https://api.open-meteo.com/v1/forecast')
FORECAST_DAYS = 8
BATCH_SIZE = 100
CACHE_S = 30 * 60


@dataclass(frozen=True)
class Conditions:
    wind_mph: float
    rain_in: float  # liquid rain in the hour, inches
    snow_in: float  # snowfall in the hour, inches


@dataclass
class Series:
    start: int  # unix time of the first hour
    wind: list
    rain: list
    snow: list

    @property
    def end(self):
        return self.start + (len(self.wind) - 1) * 3600

    def at(self, when):
        """Conditions at a moment, or None when it is outside the forecast."""
        ts = when.timestamp()
        if ts < self.start or ts > self.end:
            return None

        offset = (ts - self.start) / 3600
        i = int(offset)
        j = min(i + 1, len(self.wind) - 1)
        wind = self.wind[i] + (self.wind[j] - self.wind[i]) * (offset - i)

        # Open-Meteo precipitation is the total for the hour that *ends* at each timestamp,
        # so a moment inside an hour reads from the next row.
        k = min(i + 1 if offset > i else i, len(self.rain) - 1)
        return Conditions(round(wind, 1), self.rain[k], self.snow[k])


def snap(lat, lon, cell_deg=0.1):
    return round(round(lat / cell_deg) * cell_deg, 4), round(round(lon / cell_deg) * cell_deg, 4)


def load(cells, until):
    """Hourly series for each (lat, lon) cell up to `until`, fetching only what the cache can't cover."""
    cells = list(dict.fromkeys(cells))
    found = cache.get_many([_key(c) for c in cells])
    series = {c: s for c in cells if (s := found.get(_key(c))) and s.end >= until.timestamp()}

    # Fewer days is a smaller, faster response: a trip leaving now needs about 3 of the 8.
    days = min(max((until.date() - datetime.now(UTC).date()).days + 1, 1), FORECAST_DAYS)
    missing = [c for c in cells if c not in series]
    batches = [missing[i : i + BATCH_SIZE] for i in range(0, len(missing), BATCH_SIZE)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for fetched in pool.map(lambda batch: _fetch(batch, days), batches):
            series.update(fetched)
            cache.set_many({_key(c): s for c, s in fetched.items()}, CACHE_S)
    return series


def _key(cell):
    return f'wx:{cell[0]}:{cell[1]}'


def _fetch(cells, days=FORECAST_DAYS):
    data = get_json(
        OPEN_METEO_URL,
        {
            'latitude': ','.join(str(lat) for lat, _ in cells),
            'longitude': ','.join(str(lon) for _, lon in cells),
            'hourly': 'wind_speed_10m,rain,showers,snowfall',
            'wind_speed_unit': 'mph',
            'precipitation_unit': 'inch',
            'timezone': 'GMT',
            'timeformat': 'unixtime',
            'forecast_days': days,
        },
    )
    if isinstance(data, dict):
        data = [data]
    if len(data) != len(cells):
        raise ProviderError('Weather response does not match the requested points')

    result = {}
    for cell, item in zip(cells, data, strict=True):
        hourly = item['hourly']
        rain = [round((r or 0) + (s or 0), 3) for r, s in zip(hourly['rain'], hourly['showers'], strict=True)]
        result[cell] = Series(
            start=hourly['time'][0],
            wind=[w or 0 for w in hourly['wind_speed_10m']],
            rain=rain,
            snow=[s or 0 for s in hourly['snowfall']],
        )
    return result
