import unittest
import os
import lambda_function as lf
import json
import responses
from decimal import Decimal

class TestLambdaFunction(unittest.TestCase):

    @responses.activate
    def test_loop_items(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        data_filename = os.path.join(__location__, 'idealista_scrapper_event.json')
        with open(data_filename) as json_file:
            data = json.load(json_file)
        items = data['responsePayload']['items']

        url = 'http://api.positionstack.com/v1/forward'
        geocode_data_filename = os.path.join(__location__, 'geocode_data.json')
        with open(geocode_data_filename) as json_file:
            response_data = json.load(json_file)

        responses.add(responses.GET, url, body=json.dumps(response_data), status=200, match_querystring=False)

        parsed_data, _ = lf.items_geocode(items, 'id', 'address')
        self.assertEqual(len(items), len(parsed_data))
        for d in parsed_data:
            self.assertIsInstance(d['geo'][0]['latitude'], Decimal)
            self.assertIsInstance(d['geo'][0]['longitude'], Decimal)
            self.assertIsInstance(d['geo'][0]['confidence'], Decimal)

    @responses.activate
    def test_lambda_function(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        data_filename = os.path.join(__location__, 'idealista_scrapper_event.json')
        with open(data_filename) as json_file:
            event = json.load(json_file)

        url = 'http://api.positionstack.com/v1/forward'
        geocode_data_filename = os.path.join(__location__, 'geocode_data.json')
        with open(geocode_data_filename) as json_file:
            response_data = json.load(json_file)

        self.request_counter = 1
        def request_callback(request):
            self.request_counter += 1
            if self.request_counter == 10:
                response = dict(data=[response_data['data'][0].copy()])
                del response['data'][0]['latitude'] # make this one fail
            else:
                response = response_data
            headers = {}
            return (200, headers, json.dumps(response))
        responses.add_callback(responses.GET, url, callback=request_callback)
        #responses.add(responses.GET, url, body=json.dumps(response_data), status=200, match_querystring=False)

        result = lf.lambda_handler(event, None)
        self.assertIn('status', result)
        self.assertEqual(result['status'], 200)

    @unittest.skip("NEED TO MOCK AWS BOTO3 OR ELSE IT WRITES TO DB")
    def test_lambda_function_fail_no_property(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        data_filename = os.path.join(__location__, 'idealista_scrapper_event.json')
        with open(data_filename) as json_file:
            event = json.load(json_file)

        payload = event['responsePayload']

        expected_props = ['items', 'id_field', 'geocode_query_field']
        for prop_name in expected_props:
            prop_value = payload[prop_name]
            del payload[prop_name]
            result = lf.lambda_handler(event, None)
            self.assertIn('status', result)
            self.assertEqual(result['status'], 500)
            payload[prop_name] = prop_value
