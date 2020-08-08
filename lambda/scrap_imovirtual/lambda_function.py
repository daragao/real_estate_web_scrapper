import scrapper_imovirtual as scrapper
import json
import boto3
from decimal import Decimal


# filter and update rows needing to be created and updated
def add_updated_columns(table, items):
    id_field = 'item-id'
    id_arr = [it[id_field] for it in items]

    response = table.scan(
        AttributesToGet=[id_field,'price', 'created','price_update','date_update'],
        ScanFilter={id_field: {'AttributeValueList': id_arr, 'ComparisonOperator': 'IN'}}
    )
    scanned_items = response['Items']

    #array to hash to be faster to look
    old_items_map = { }
    for it in scanned_items:
        old_items_map[it[id_field]] = it
        if 'price_update' not in it[id_field]:
            it['price_update'] = [Decimal(it['price'])]
        if 'date_update' not in it[id_field]:
            it['date_update'] = [it['created']]

    new_items = [] # items that have been updated or are  new
    # rows with new price get and updated array
    for it in items:
        if it[id_field] in old_items_map:
            # this item is already in the DB
            old_item = old_items_map[it[id_field]]
            if it['price'] != old_item['price']:
                # price has been updated
                old_item['price_update'].append(Decimal(it['price']))
                old_item['date_update'].append(it['created'])
                it['price_update'] = old_item['price_update']
                it['date_update'] = old_item['date_update']
                new_items.append(it)
                print('Price update!\n\t{}\n\t{}'.format(it, old_items_map[it[id_field]]))
        else:
            # this item is not in the DB
            new_items.append(it)
    return new_items

def put_items(table, items):
    print('Put {} items into table'.format(len(items)))
    with table.batch_writer() as batch:
        for it in items:
            batch.put_item(Item=it)


def lambda_handler(event, context):
    print('Received event: {}'.format(event))

    items = scrapper.scrap_imovirtual()

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('imovirtual_scrap')
    new_items = add_updated_columns(table, items)
    put_items(table, new_items)

    return { 'status': 200, 'items': items }

class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(CustomJsonEncoder, self).default(obj)

