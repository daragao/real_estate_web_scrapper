import scrapper
import boto3
import json

def add_updated_columns(items):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('scrapped_ads')

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
    table = dynamodb.Table('scrapped_ads')

    items = scrapper.scrap()

    #add array with updated prices
    items = add_updated_columns(items)

    # overwrites old values
    # TODO: have an array of changed values
    with table.batch_writer() as batch:
        for it in items:
            batch.put_item(Item=it)

    return { 'status': 200, 'items': items }
