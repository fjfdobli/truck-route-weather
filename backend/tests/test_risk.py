from django.test import SimpleTestCase

from risk import Risk, assess, intensity, wind_risk
from weather import Conditions

L, M, H, S, N = Risk.LOW, Risk.MODERATE, Risk.HIGH, Risk.SEVERE, Risk.NO_TRAVEL
LIGHT = 10_000


def level(wind=0, rain=0, snow=0, weight=LIGHT):
    return assess(Conditions(wind, rain, snow), weight).level


class WindTests(SimpleTestCase):
    def test_bands(self):
        cases = [(0, L), (24.9, L), (25, M), (34.9, M), (35, H), (44.9, H), (45, S), (54.9, S), (55, N), (80, N)]
        for wind, expected in cases:
            with self.subTest(wind=wind):
                self.assertEqual(level(wind=wind), expected)


class RainTests(SimpleTestCase):
    def test_bands(self):
        cases = [(0.09, L), (0.10, M), (0.24, M), (0.25, H), (0.49, H), (0.50, S), (1.00, S), (1.01, N)]
        for rain, expected in cases:
            with self.subTest(rain=rain):
                self.assertEqual(level(rain=rain), expected)


class SnowTests(SimpleTestCase):
    def test_bands(self):
        cases = [(0.4, L), (0.5, M), (0.9, M), (1.0, H), (1.9, H), (2.0, S), (3.0, S), (3.1, N)]
        for snow, expected in cases:
            with self.subTest(snow=snow):
                self.assertEqual(level(snow=snow), expected)


class LoadRuleTests(SimpleTestCase):
    def test_55_mph_is_no_travel_for_any_load(self):
        self.assertEqual(wind_risk(55, 0), N)

    def test_45_to_54_mph_over_30k_lb_is_no_travel(self):
        self.assertEqual(wind_risk(45, 30_000), S)
        self.assertEqual(wind_risk(45, 30_001), N)
        self.assertEqual(wind_risk(54.9, 45_000), N)

    def test_35_to_44_mph_over_40k_lb_is_severe(self):
        self.assertEqual(wind_risk(35, 40_000), H)
        self.assertEqual(wind_risk(35, 40_001), S)
        self.assertEqual(wind_risk(44.9, 80_000), S)

    def test_heavy_load_alone_does_not_raise_light_wind(self):
        self.assertEqual(wind_risk(34.9, 80_000), M)

    def test_flags_when_load_made_it_worse(self):
        self.assertTrue(assess(Conditions(40, 0, 0), 50_000).load_raised)
        self.assertFalse(assess(Conditions(40, 0, 0), 20_000).load_raised)


class IntensityTests(SimpleTestCase):
    def score(self, wind=0, rain=0, snow=0, weight=LIGHT):
        return intensity(Conditions(wind, rain, snow), weight)

    def test_runs_through_each_band(self):
        self.assertEqual(self.score(wind=12.5), 0.5)
        self.assertEqual(self.score(wind=40), 2.5)
        self.assertEqual(self.score(rain=0.375), 2.5)
        self.assertEqual(self.score(wind=60), 4)

    def test_never_crosses_into_the_next_level_early(self):
        self.assertEqual(self.score(rain=1.0), 3.99)

    def test_load_rule_lifts_the_score(self):
        self.assertEqual(self.score(wind=40, weight=50_000), 3)
        self.assertEqual(self.score(wind=50, weight=35_000), 4)


class CombinedTests(SimpleTestCase):
    def test_worst_condition_wins(self):
        result = assess(Conditions(wind_mph=30, rain_in=0.3, snow_in=2.5), LIGHT)
        self.assertEqual((result.wind, result.rain, result.snow, result.level), (M, H, S, S))

    def test_no_forecast_means_no_assessment(self):
        self.assertIsNone(assess(None, LIGHT))

    def test_labels(self):
        self.assertEqual(N.label, 'No Travel')
        self.assertEqual(M.label, 'Moderate')
