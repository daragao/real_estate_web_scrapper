import idealista_client
import boto3
import json
from datetime import datetime
from decimal import Decimal

def add_updated_columns(table, items):
    response = table.scan(
        AttributesToGet=['id','price', 'created','price_update','date_update'],
        ScanFilter={'id': {'AttributeValueList': [it['id'] for it in items],'ComparisonOperator': 'IN'}}
    )
    scanned_items = response['Items']

    #array to hash to be faster to look
    old_items_map = { }
    for it in scanned_items:
        if 'price_update' not in it['id']:
            it['price_update'] = [it['price']]
        if 'date_update' not in it['id']:
            it['date_update'] = [it['created']]
        old_items_map[it['id']] = it

    # rows with new price get and updated array
    for it in items:
        if it['id'] in old_items_map and it['price'] != old_items_map[it['id']]['price']:
            old_items_map[it['id']]['price_update'].append(it['price'])
            old_items_map[it['id']]['date_update'].append(it['created'])
            it['price_update'] = old_items_map[it['id']]['price_update']
            it['date_update'] = old_items_map[it['id']]['date_update']
            print('Price update!\n\t{}\n\t{}'.format(it, old_items_map[it['id']]))
    return items

def lambda_handler(event, context):
    print('Received event: {}'.format(event))

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('idealista_ads')

    host = 'https://api.idealista.com'
    secret_token = idealista_client.load_secret()
    headers_token = idealista_client.request_oauth(host, secret_token)
    data = idealista_client.request_data(host, headers_token)

    ads = []
    for page in data:
        ads += page['elementList']
    for ad in ads:
        ad['id'] = ad['propertyCode']
        ad['created'] = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        ad['price'] = Decimal(str(ad['price']))
        ad['size'] = Decimal(str(ad['size']))
        ad['rooms'] = Decimal(str(ad['rooms']))
        ad['bathrooms'] = Decimal(str(ad['bathrooms']))
        ad['latitude'] = Decimal(str(ad['latitude']))
        ad['longitude'] = Decimal(str(ad['longitude']))
        ad['priceByArea'] = Decimal(str(ad['priceByArea']))
        ad['numPhotos'] = Decimal(str(ad['numPhotos']))
        ad['bathrooms'] = Decimal(str(ad['bathrooms']))

    add_updated_columns(table, ads)

    # overwrites old values
    # TODO: have an array of changed values
    with table.batch_writer() as batch:
        for it in ads:
            batch.put_item(Item=it)

    return { 'status': 200, 'items': ads }
