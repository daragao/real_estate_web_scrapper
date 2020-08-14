import requests
import json
import time
from decimal import Decimal
import os

def load_secret():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    secret_filename = os.path.join(__location__, 'secret.json')
    with open(secret_filename) as json_file:
        secret = json.load(json_file)
    print('Loaded secret json:\n\tpositionstack: {}'.format(secret['positionstack']))
    return secret


def get_geocode(key, query, country, region):
    url = 'http://api.positionstack.com/v1/forward?access_key={}&query={}&country={}&region={}'.format(key,query,country,region)
    print('\tURL: {}'.format(url))
    req = requests.get(url)
    print('\tHTTP CODE: {}'.format(req.status_code))
    if(req.status_code != 200):
        print("BAD STATUS CODE: {}\nResponse Text:\n{}".format(req.status_code, req.text))
        return { 'error': { 'status_code': req.status_code, 'body': req.text } }
    geo_data = req.json()
    return geo_data

def parse_geocode_data(geo_data):
    # dynamo demands that  the floats are Decimal
    for g in geo_data['data']:
        if 'latitude' not in g or 'longitude' not in g or 'confidence' not in g:
            print('Failed to parse geo:\n\t{}'.format(g))
            g['parsing_failed'] = True
            continue
        g['latitude'] = Decimal(str(g['latitude']))
        g['longitude'] = Decimal(str(g['longitude']))
        g['confidence'] = Decimal(str(g['confidence']))
    return geo_data['data']
