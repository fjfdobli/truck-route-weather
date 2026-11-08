from datetime import UTC, datetime

from django.test import SimpleTestCase

from common.geo import METERS_PER_MILE
from planner.heatmap import HOURS, MAX_CELLS, Heatmap, corridor, fill
from routing import Route
from weather import Series

START = datetime(2026, 11, 9, tzinfo=UTC)


def straight_route(miles):
    coords = [(40 + i * 0.0145, -100.0) for i in range(miles + 1)]
    return Route(coords, [METERS_PER_MILE] * miles, [60] * miles)


class CorridorTests(SimpleTestCase):
    def test_cells_surround_the_route(self):
        cell_deg, cells = corridor([straight_route(100)])
        self.assertEqual(cell_deg, 0.3)
        lons = sorted({lon for _, lon in cells})
        self.assertEqual(lons, [-100.2, -99.9, -99.6])

    def test_long_trips_use_bigger_cells(self):
        miles = 1500
        diagonal = Route(
            [(30 + i * 0.01, -120 + i * 0.013) for i in range(miles + 1)],
            [METERS_PER_MILE] * miles,
            [60] * miles,
        )
        cell_deg, cells = corridor([diagonal])
        self.assertGreater(cell_deg, 0.3)
        self.assertLessEqual(len(cells), MAX_CELLS)


class FillTests(SimpleTestCase):
    def test_one_row_per_hour_and_none_past_forecast(self):
        cells = [(40.0, -100.0)]
        hours = 10
        series = {cells[0]: Series(int(START.timestamp()), [40] * hours, [0] * hours, [0] * hours)}
        heatmap = fill(Heatmap(START, 0.25, cells), series, 10_000)

        self.assertEqual(len(heatmap.values), HOURS + 1)
        self.assertEqual(heatmap.values[0], [2.5])
        self.assertIsNone(heatmap.values[HOURS][0])
