from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase

from weather import Series, load, snap

START = datetime(2026, 11, 9, 0, tzinfo=UTC)


def series():
    return Series(
        start=int(START.timestamp()),
        wind=[10, 20, 30, 40],
        rain=[0.0, 0.1, 0.2, 0.3],
        snow=[0.0, 0.0, 1.0, 0.0],
    )


class SeriesTests(SimpleTestCase):
    def test_on_the_hour(self):
        wx = series().at(START + timedelta(hours=1))
        self.assertEqual((wx.wind_mph, wx.rain_in), (20, 0.1))

    def test_wind_is_interpolated(self):
        self.assertEqual(series().at(START + timedelta(minutes=90)).wind_mph, 25)

    def test_precipitation_uses_the_hour_being_driven(self):
        # 01:30 sits in the 01:00-02:00 hour, which Open-Meteo stamps at 02:00.
        wx = series().at(START + timedelta(minutes=90))
        self.assertEqual((wx.rain_in, wx.snow_in), (0.2, 1.0))

    def test_outside_forecast_is_none(self):
        self.assertIsNone(series().at(START - timedelta(minutes=1)))
        self.assertIsNone(series().at(START + timedelta(hours=3, minutes=1)))

    def test_snap_groups_nearby_points(self):
        self.assertEqual(snap(41.8762, -87.6243), snap(41.9149, -87.6481))
        self.assertEqual(snap(41.8762, -87.6243), (41.9, -87.6))


CELL = (40.0, -100.0)


def hours_from_now(hours):
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    return {CELL: Series(int(now.timestamp()), [5] * hours, [0.0] * hours, [0.0] * hours)}


class LoadTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_asks_only_for_the_days_the_trip_needs(self):
        with patch('weather.openmeteo._fetch', return_value=hours_from_now(96)) as fetch:
            load([CELL], datetime.now(UTC) + timedelta(hours=50))
        self.assertIn(fetch.call_args.args[1], (3, 4))

    def test_reuses_the_cache_only_when_it_covers_the_trip(self):
        with patch('weather.openmeteo._fetch', return_value=hours_from_now(30)) as fetch:
            load([CELL], datetime.now(UTC) + timedelta(hours=20))
            load([CELL], datetime.now(UTC) + timedelta(hours=20))
            self.assertEqual(fetch.call_count, 1)
            load([CELL], datetime.now(UTC) + timedelta(hours=60))
            self.assertEqual(fetch.call_count, 2)
