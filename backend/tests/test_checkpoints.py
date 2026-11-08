from datetime import UTC, datetime, timedelta

from django.test import SimpleTestCase

from common.geo import METERS_PER_MILE
from planner import place_checkpoints
from routing import Route

DEPART = datetime(2026, 11, 9, 14, tzinfo=UTC)
MILE = METERS_PER_MILE


def straight_route(miles, mph=60):
    # One point per mile going north, driven at a steady speed.
    coords = [(30 + i * 0.0145, -95.0) for i in range(miles + 1)]
    return Route(coords, [MILE] * miles, [3600 / mph] * miles)


class CheckpointTests(SimpleTestCase):
    def test_places_start_every_interval_and_end(self):
        cps = place_checkpoints(straight_route(60), 25, DEPART)
        self.assertEqual([round(cp.mile) for cp in cps], [0, 25, 50, 60])

    def assertAfter(self, cp, minutes):
        self.assertAlmostEqual((cp.eta - DEPART) / timedelta(minutes=1), minutes, places=3)

    def test_eta_follows_driving_time(self):
        cps = place_checkpoints(straight_route(60, mph=50), 25, DEPART)
        self.assertAfter(cps[1], 30)
        self.assertAfter(cps[-1], 72)

    def test_truck_speed_cap(self):
        cps = place_checkpoints(straight_route(65, mph=80), 50, DEPART)
        self.assertAfter(cps[-1], 60)

    def test_coverage_adds_up_to_trip(self):
        cps = place_checkpoints(straight_route(137), 10, DEPART)
        self.assertAlmostEqual(sum(cp.covers_mi for cp in cps), 137)

    def test_short_trip_has_start_and_end(self):
        cps = place_checkpoints(straight_route(8), 25, DEPART)
        self.assertEqual([round(cp.mile) for cp in cps], [0, 8])

    def test_checkpoint_on_exact_end_is_not_duplicated(self):
        cps = place_checkpoints(straight_route(50), 25, DEPART)
        self.assertEqual([round(cp.mile) for cp in cps], [0, 25, 50])
