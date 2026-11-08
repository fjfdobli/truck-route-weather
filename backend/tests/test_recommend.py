from types import SimpleNamespace

from django.test import SimpleTestCase

from planner import explain, summarize, warning
from risk import Risk


def cp(level, miles):
    risk = None if level is None else SimpleNamespace(level=level)
    return SimpleNamespace(risk=risk, covers_mi=miles)


def route(hours, **miles):
    levels = {'low': Risk.LOW, 'high': Risk.HIGH, 'severe': Risk.SEVERE, 'no_travel': Risk.NO_TRAVEL}
    cps = [cp(levels[name], m) for name, m in miles.items()]
    return summarize(cps, hours)


def best_of(*summaries):
    return min(range(len(summaries)), key=lambda i: summaries[i].sort_key())


class SummaryTests(SimpleTestCase):
    def test_miles_and_mile_weighted_average(self):
        s = route(5, low=75, high=25)
        self.assertEqual((s.miles(Risk.LOW), s.miles(Risk.HIGH)), (75, 25))
        self.assertAlmostEqual(s.avg_risk, 0.5)

    def test_unrated_miles_stay_out_of_the_average(self):
        s = summarize([cp(Risk.HIGH, 10), cp(None, 90)], 3)
        self.assertEqual((s.unknown_mi, s.avg_risk), (90, 2))


class RankingTests(SimpleTestCase):
    def test_fewest_severe_miles_beats_a_faster_route(self):
        self.assertEqual(best_of(route(4, low=90, severe=10), route(6, low=100)), 1)

    def test_then_fewest_high_miles(self):
        self.assertEqual(best_of(route(4, low=80, high=20), route(5, low=95, high=5)), 1)

    def test_then_lowest_average_risk(self):
        a = route(4, low=50, high=10)
        b = route(5, low=90, high=10)
        self.assertEqual(best_of(a, b), 1)

    def test_then_shortest_time(self):
        self.assertEqual(best_of(route(6, low=100), route(5, low=120)), 1)

    def test_no_travel_miles_count_as_severe(self):
        self.assertEqual(best_of(route(4, low=90, no_travel=10), route(9, low=95, severe=5)), 1)

    def test_a_clean_route_beats_any_no_travel(self):
        self.assertEqual(best_of(route(4, low=99, no_travel=1), route(9, low=50, high=50)), 1)


class WarningTests(SimpleTestCase):
    def test_flags_no_travel_on_the_recommended_route(self):
        best = route(4, low=90, no_travel=3)
        self.assertIn('crosses 3 miles of No Travel', warning([best, route(5, low=80, severe=20)], best))

    def test_quiet_when_the_recommended_route_is_clear(self):
        best = route(4, low=100)
        self.assertIsNone(warning([best, route(5, low=99, no_travel=1)], best))


class ExplainTests(SimpleTestCase):
    def test_names_the_rule_that_decided(self):
        text = explain(route(6, low=100), route(4, low=90, severe=10))
        self.assertIn('Fewest Severe or No Travel miles: 0 against 10', text)

    def test_time_when_weather_ties(self):
        text = explain(route(4, low=100), route(5.5, low=100))
        self.assertIn('1.5 hours faster', text)
