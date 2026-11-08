from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase

from common.http import ProviderError
from routing import geocode

PHOTON = {
    'features': [
        {
            'geometry': {'coordinates': [-97.74, 30.27]},
            'properties': {'name': 'Austin', 'state': 'Texas', 'countrycode': 'US'},
        },
    ]
}
OPEN_METEO = {
    'results': [
        {'name': 'Austin', 'admin1': 'Minnesota', 'country_code': 'US', 'latitude': 43.67, 'longitude': -92.97},
        {'name': 'Austin', 'admin1': 'Texas', 'country_code': 'US', 'latitude': 30.27, 'longitude': -97.74},
        {'name': 'Austin', 'admin1': 'Tasmania', 'country_code': 'AU', 'latitude': -41.0, 'longitude': 146.0},
    ]
}


def provider(photon=PHOTON, open_meteo=OPEN_METEO):
    def fake(url, params=None, **_):
        source = photon if url == geocode.PHOTON_URL else open_meteo
        if isinstance(source, Exception):
            raise source
        return source

    return fake


class GeocodeTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_uses_photon_when_it_answers(self):
        with patch('routing.geocode.get_json', side_effect=provider()) as get_json:
            places = geocode.search('austin')
        self.assertEqual(places[0].label, 'Austin, Texas, US')
        self.assertEqual(get_json.call_count, 1)

    def test_falls_back_when_photon_fails(self):
        with patch('routing.geocode.get_json', side_effect=provider(photon=ProviderError('down'))):
            places = geocode.search('austin')
        self.assertEqual([p.label for p in places], ['Austin, Minnesota, US', 'Austin, Texas, US'])

    def test_skips_photon_for_a_while_after_a_failure(self):
        with patch('routing.geocode.get_json', side_effect=provider(photon=ProviderError('down'))):
            geocode.search('austin')
        with patch('routing.geocode.get_json', side_effect=provider()) as get_json:
            geocode.search('dallas')
        self.assertEqual(get_json.call_args.args[0], geocode.FALLBACK_URL)

    def test_fallback_ranks_places_matching_the_text_after_a_comma(self):
        with patch('routing.geocode.get_json', side_effect=provider(photon=ProviderError('down'))) as get_json:
            places = geocode.search('Austin, Texas')
        self.assertEqual(places[0].label, 'Austin, Texas, US')
        self.assertEqual(get_json.call_args.args[1]['name'], 'austin')

    def test_fails_only_when_both_providers_fail(self):
        failing = provider(photon=ProviderError('down'), open_meteo=ProviderError('also down'))
        with patch('routing.geocode.get_json', side_effect=failing), self.assertRaises(ProviderError):
            geocode.search('austin')
