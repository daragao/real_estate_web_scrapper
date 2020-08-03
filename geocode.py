###############################################################################################################
import json
import geocode
import boto3

def lambda_handler(event, context):
    print('Received event: {}'.format(event))
    geocode.geocode(event['items'])

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('scrapped_ads')
    # overwrites old values
    # TODO: have an array of changed values
    with table.batch_writer() as batch:
        for it in event['items']:
            batch.put_item(Item=it)

    return {
        'statusCode': 200,
        'event': event,
        'body': json.dumps('Hello from Lambda!')
    }
###############################################################################################################

import requests
import json
import urllib
import time

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
        if(len(ad['geo']) != 0 and len(ad['geo'][0]) == 0):
            print('FAILED!!!!!\n\t{}'.format(geo_data))
        i += 1
        time.sleep(2) #some requests come empty maybe I am breaking the rate limit
        if((i % 10) == 0):
            print('{} requests made (sleeping...)'.format(i))

