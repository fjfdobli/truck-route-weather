from datetime import timedelta
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils import timezone

from common.geo import METERS_PER_MILE
from common.http import ProviderError
from routing import NoRouteError, Route
from weather import Series

CALM_LON = -100.0
WINDY_LON = -101.0


def route_north(lon, miles, mph):
    coords = [(35 + i * 0.0145, lon) for i in range(miles + 1)]
    return Route(coords, [METERS_PER_MILE] * miles, [3600 / mph] * miles, name=f'Road {lon}')


def fake_weather(cells):
    start = int((timezone.now() - timedelta(hours=2)).timestamp()) // 3600 * 3600
    hours = 80
    series = {}
    for lat, lon in cells:
        wind = 40 if lon <= WINDY_LON + 0.3 else 8
        series[(lat, lon)] = Series(start, [wind] * hours, [0.0] * hours, [0.0] * hours)
    return series


def plan_body(**overrides):
    body = {
        'origin': {'label': 'A', 'lat': 35.0, 'lon': CALM_LON},
        'destination': {'label': 'B', 'lat': 35.87, 'lon': CALM_LON},
        'departure': (timezone.now() + timedelta(hours=1)).isoformat(),
        'weight_lb': 45_000,
        'interval_mi': 10,
    }
    body.update(overrides)
    return body


@patch('planner.service.weather.load', side_effect=fake_weather)
@patch('planner.service.routing.find_routes')
class PlanEndpointTests(SimpleTestCase):
    def post(self, body):
        return self.client.post('/api/plan', body, content_type='application/json')

    def test_safer_route_beats_faster_windy_route(self, find_routes, _load):
        calm_slow = route_north(CALM_LON, 60, mph=50)
        windy_fast = route_north(WINDY_LON, 60, mph=65)
        find_routes.return_value = [windy_fast, calm_slow]

        response = self.post(plan_body())

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['recommended_id'], 1)
        self.assertIn('Fewest Severe or No Travel miles', data['reason'])

        windy = data['routes'][0]
        self.assertEqual(windy['rank'], 2)
        self.assertAlmostEqual(windy['summary']['severe_mi'], 60, delta=0.5)
        self.assertTrue(windy['checkpoints'][1]['risk']['load_raised'])
        self.assertEqual(windy['checkpoints'][1]['risk']['level'], 'Severe')

    def test_light_load_keeps_wind_at_high(self, find_routes, _load):
        find_routes.return_value = [route_north(WINDY_LON, 30, mph=60)]

        data = self.post(plan_body(weight_lb=20_000)).json()

        checkpoint = data['routes'][0]['checkpoints'][1]
        self.assertEqual(checkpoint['risk']['level'], 'High')
        self.assertFalse(checkpoint['risk']['load_raised'])

    def test_response_includes_a_48_hour_heatmap(self, find_routes, _load):
        find_routes.return_value = [route_north(CALM_LON, 40, mph=60)]

        heatmap = self.post(plan_body()).json()['heatmap']

        self.assertEqual(len(heatmap['values']), 49)
        self.assertEqual(len(heatmap['values'][0]), len(heatmap['cells']))

    def test_checkpoints_follow_the_requested_interval(self, find_routes, _load):
        find_routes.return_value = [route_north(CALM_LON, 60, mph=60)]

        data = self.post(plan_body(interval_mi=25)).json()

        self.assertEqual([round(cp['mile']) for cp in data['routes'][0]['checkpoints']], [0, 25, 50, 60])

    def test_provider_failure_returns_502(self, find_routes, _load):
        find_routes.side_effect = ProviderError('router.example is busy')

        response = self.post(plan_body())

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()['detail'], 'router.example is busy')

    def test_no_road_between_places_returns_422(self, find_routes, _load):
        find_routes.side_effect = NoRouteError('No road connects these two places.')

        response = self.post(plan_body())

        self.assertEqual(response.status_code, 422)
        self.assertIn('No road connects', response.json()['detail'])

    def test_places_outside_north_america_are_field_errors(self, find_routes, _load):
        davao = {'label': 'Davao City', 'lat': 7.07, 'lon': 125.61}

        response = self.post(plan_body(origin=davao))

        self.assertEqual(response.status_code, 400)
        self.assertIn('US, Canada and Mexico', response.json()['origin'][0])
        find_routes.assert_not_called()


class PlanValidationTests(SimpleTestCase):
    def post(self, body):
        return self.client.post('/api/plan', body, content_type='application/json')

    def test_past_departure_is_rejected(self):
        past = (timezone.now() - timedelta(hours=3)).isoformat()
        response = self.post(plan_body(departure=past))
        self.assertEqual(response.status_code, 400)
        self.assertIn('departure', response.json())

    def test_departure_beyond_forecast_is_rejected(self):
        later = (timezone.now() + timedelta(days=6)).isoformat()
        self.assertEqual(self.post(plan_body(departure=later)).status_code, 400)

    def test_interval_must_be_10_25_or_50(self):
        response = self.post(plan_body(interval_mi=15))
        self.assertEqual(response.status_code, 400)
        self.assertIn('interval_mi', response.json())

    def test_weight_is_required(self):
        body = plan_body()
        del body['weight_lb']
        self.assertIn('weight_lb', self.post(body).json())

    def test_lat_without_lon_is_rejected(self):
        response = self.post(plan_body(origin={'label': 'A', 'lat': 35.0}))
        self.assertEqual(response.status_code, 400)
