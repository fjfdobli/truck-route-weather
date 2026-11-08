from types import SimpleNamespace

from django.test import SimpleTestCase

import weather
from planner.service import MAX_CHECKPOINT_CELLS, checkpoint_grid


def checkpoints_along(miles, every_mi):
    # A diagonal line, roughly one checkpoint per `every_mi` miles.
    step = every_mi / 69
    return [
        SimpleNamespace(lat=30 + i * step * 0.6, lon=-120 + i * step * 0.8) for i in range(int(miles / every_mi) + 1)
    ]


class CheckpointGridTests(SimpleTestCase):
    def test_short_trips_keep_the_finest_grid(self):
        self.assertEqual(checkpoint_grid(checkpoints_along(250, 10)), 0.1)

    def test_coast_to_coast_stays_within_the_budget(self):
        cps = checkpoints_along(2900, 10) * 3
        grid = checkpoint_grid(cps)
        cells = {weather.snap(cp.lat, cp.lon, grid) for cp in cps}
        self.assertGreater(grid, 0.1)
        self.assertLessEqual(len(cells), MAX_CHECKPOINT_CELLS)
