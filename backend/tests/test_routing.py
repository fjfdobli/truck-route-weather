from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase

from common.geo import Point
from common.http import ProviderError
from routing import NoRouteError, Route, find_routes
from routing.models import name_apart, road_ref
from routing.valhalla import _parse, decode

A, B = Point(35.0, -100.0), Point(36.0, -100.0)


def encode(coords, precision=6):
    out, last = [], (0, 0)
    for lat, lon in coords:
        point = (round(lat * 10**precision), round(lon * 10**precision))
        for delta in (point[0] - last[0], point[1] - last[1]):
            value = ~(delta << 1) if delta < 0 else delta << 1
            while value >= 0x20:
                out.append(chr((0x20 | (value & 0x1F)) + 63))
                value >>= 5
            out.append(chr(value + 63))
        last = point
    return ''.join(out)


def road(lon, hours):
    coords = [(35.0, lon), (35.5, lon), (36.0, lon)]
    return Route(coords, [55_000, 55_000], [hours * 1800, hours * 1800])


class ValhallaParseTests(SimpleTestCase):
    def test_decodes_google_polyline(self):
        coords = decode('_p~iF~ps|U_ulLnnqC_mqNvxq`@', precision=5)
        self.assertEqual(coords, [(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)])

    def test_spreads_maneuver_time_over_its_segments_by_length(self):
        shape = [(35.0, -100.0), (35.1, -100.0), (35.4, -100.0), (35.5, -100.0)]
        trip = {
            'legs': [
                {
                    'shape': encode(shape),
                    'maneuvers': [
                        {
                            'begin_shape_index': 0,
                            'end_shape_index': 2,
                            'time': 400,
                            'length': 44,
                            'street_names': ['I 35'],
                        },
                        {
                            'begin_shape_index': 2,
                            'end_shape_index': 3,
                            'time': 100,
                            'length': 11,
                            'street_names': ['Main St'],
                        },
                    ],
                }
            ]
        }
        route = _parse(trip, [])
        self.assertEqual(route.profile, 'truck')
        self.assertEqual(len(route.segment_m), 3)
        self.assertAlmostEqual(route.segment_s[0], 100, delta=1)
        self.assertAlmostEqual(route.segment_s[1], 300, delta=1)
        self.assertAlmostEqual(route.duration_s, 500)
        self.assertEqual(route.name, 'I 35')

    def test_joins_legs_without_repeating_the_via_point(self):
        def leg(a, b):
            step = {'begin_shape_index': 0, 'end_shape_index': 1, 'time': 60, 'length': 1}
            return {'shape': encode([a, b]), 'maneuvers': [step]}

        route = _parse({'legs': [leg((35, -100), (35.5, -100)), leg((35.5, -100), (36, -100))]}, [])
        self.assertEqual(route.coords, [(35, -100), (35.5, -100), (36, -100)])
        self.assertEqual(route.segment_s, [60, 60])

    def test_routes_with_the_same_main_roads_get_different_names(self):
        a = Route([], [], [], 'I 86 / I 90', roads={'I 86': 90, 'I 90': 80, 'NY 17': 30})
        b = Route([], [], [], 'I 86 / I 90', roads={'I 86': 95, 'I 90': 70, 'US 20': 40})
        c = Route([], [], [], 'I 90 / I 690', roads={'I 90': 200, 'I 690': 20})
        name_apart([a, b, c])
        self.assertEqual([a.name, b.name, c.name], ['I 86 / NY 17', 'I 86 / US 20', 'I 90 / I 690'])

    def test_road_ref_takes_the_number_not_the_direction(self):
        self.assertEqual(road_ref('US 30 West'), 'US 30')
        self.assertEqual(road_ref('I 80'), 'I 80')
        self.assertIsNone(road_ref('Dwight D. Eisenhower Highway'))


class FindRoutesTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    @patch('routing.service.osrm.fetch_routes')
    @patch('routing.service.valhalla.fetch_routes')
    def test_uses_truck_routes_and_rounds_the_load_up(self, truck, car):
        truck.return_value = [road(-100.0, 2), road(-100.5, 2.5), road(-101.0, 3)]
        routes = find_routes(A, B, 45_200)
        self.assertEqual(len(routes), 3)
        self.assertEqual(truck.call_args.kwargs['weight_lb'], 46_000)
        car.assert_not_called()

    @patch('routing.service.osrm.fetch_routes')
    @patch('routing.service.valhalla.fetch_routes', side_effect=ProviderError('too far'))
    def test_falls_back_to_car_routes(self, _truck, car):
        car.return_value = [road(-100.0, 2), road(-100.5, 2.5), road(-101.0, 3)]
        self.assertEqual(len(find_routes(A, B, 45_000)), 3)

    @patch('routing.service.osrm.fetch_routes')
    @patch('routing.service.valhalla.fetch_routes', side_effect=NoRouteError('no road'))
    def test_no_road_is_final(self, _truck, car):
        with self.assertRaises(NoRouteError):
            find_routes(A, B, 45_000)
        car.assert_not_called()
