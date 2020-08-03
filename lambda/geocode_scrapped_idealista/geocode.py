
import requests
import json
import urllib
import time
from decimal import Decimal

def geocode(items):
    with open("secret.json") as json_file:
        secret = json.load(json_file)
    print('Loaded secret json:\n\tpositionstack: {}'.format(secret['positionstack']))

    key = secret['positionstack']['key']

    country = "PT"
    region = "Lisboa"

    for i, ad in enumerate(items):
        print('{}) --------------'.format(i))
        address = ad['address']
        url = 'http://api.positionstack.com/v1/forward?access_key={}&query={}&country={}&region={}'.format(key,address,country,region)
        print('\tQuery address: {}\n\tURL: {}'.format(urllib.parse.unquote(address),url))
        req = requests.get(url)
        print('\tHTTP CODE: {}'.format(req.status_code))
        if(req.status_code != 200):
            print("!!!!!!BAD STATUS CODE!!!!!")
        geo_data = req.json()
        ad['geo'] = geo_data['data']
        
        # apparently dynamoDB does not like floats
        for g in ad['geo']:
            g['latitude'] = Decimal(str(g['latitude']))
            g['longitude'] = Decimal(str(g['longitude']))
            g['confidence'] = Decimal(str(g['confidence']))
        
        if(len(ad['geo']) != 0 and len(ad['geo'][0]) == 0):
            print('FAILED!!!!!\n\t{}'.format(geo_data))
            
        i += 1
        time.sleep(2) #some requests come empty maybe I am breaking the rate limit
        if((i % 10) == 0):
            print('{} requests made (sleeping...)'.format(i))
