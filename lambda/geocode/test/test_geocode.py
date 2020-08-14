import unittest
import os
import geocode
import json
import responses
from decimal import Decimal

class TestGeocode(unittest.TestCase):

    def setUp(self):
        pass

    def test_load_secret(self):
        secret = geocode.load_secret()
        expected_attr = ['api_key', 'secret', 'positionstack']
        for attr_name in expected_attr:
            self.assertTrue(attr_name in secret)

    @responses.activate
    def test_geocode_data(self):
        url = 'http://api.positionstack.com/v1/forward?access_key=81b633155ad885d61fbd4123bae2e096&query=Largo Maria Leonor&country=PT&region=Lisboa'
        responses.add(responses.GET, url, body='{}', status=200)

        secret = geocode.load_secret()
        key = secret['positionstack']['key']
        data = geocode.get_geocode(key, 'Largo Maria Leonor', 'PT', 'Lisboa')
        self.assertIsNotNone(data)

    @responses.activate
    def test_geocode_data_fail(self):
        url = 'http://api.positionstack.com/v1/forward?access_key=81b633155ad885d61fbd4123bae2e096&query=Largo Maria Leonor&country=PT&region=Lisboa'
        responses.add(responses.GET, url, body='{}', status=400)

        secret = geocode.load_secret()
        key = secret['positionstack']['key']
        data = geocode.get_geocode(key, 'Largo Maria Leonor', 'PT', 'Lisboa')
        self.assertIn('error', data)

    def test_parse_geocode(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        data_filename = os.path.join(__location__, 'geocode_data.json')
        with open(data_filename) as json_file:
            data = json.load(json_file)
        parsed_data = geocode.parse_geocode_data(data)
        for d in parsed_data:
            self.assertNotIn('parsing_failed', parsed_data[0])
            self.assertIsInstance(d['latitude'], Decimal)
            self.assertIsInstance(d['longitude'], Decimal)
            self.assertIsInstance(d['confidence'], Decimal)

    def test_parse_geocode_fail(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        data_filename = os.path.join(__location__, 'geocode_data.json')
        with open(data_filename) as json_file:
            data = json.load(json_file)
        del data['data'][0]['latitude'] # break this geo
        parsed_data = geocode.parse_geocode_data(data)
        self.assertNotIn('latitude', parsed_data[0])
        self.assertIn('parsing_failed', parsed_data[0])
        self.assertTrue(parsed_data[0]['parsing_failed'])
        for d in parsed_data[1:]: # all the other elements should be good
            self.assertNotIn('parsing_failed', parsed_data[0])
            self.assertIsInstance(d['latitude'], Decimal)
            self.assertIsInstance(d['longitude'], Decimal)
            self.assertIsInstance(d['confidence'], Decimal)
