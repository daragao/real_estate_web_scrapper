import geocode
import urllib
import boto3

def items_geocode(items, id_field, query_field):
    secret = geocode.load_secret()
    key = secret['positionstack']['key']

    memo_geocode = {}
    result = []
    for it in items:
        geocode_key = '{}-{}-{}'.format(it[query_field], 'PT', 'Lisboa')
        if geocode_key in memo_geocode:
            geo = memo_geocode[geocode_key]
        else:
            geo = geocode.get_geocode(key, it[query_field], 'PT', 'Lisboa')
            parsed_geo = geocode.parse_geocode_data(geo)
            memo_geocode[geocode_key] = parsed_geo
        result.append({ id_field: it[id_field], 'geo': parsed_geo })
    return result, memo_geocode

def put_items(table, items):
    print('Put {} items into table'.format(len(items)))
    with table.batch_writer() as batch:
        for it in items:
            batch.put_item(Item=it)

def lambda_handler(event, context):
    if 'responsePayload' in event:
        payload = event['responsePayload']
    else:
        payload = event['Input']['Payload']
    if 'items' not in payload:
        return { 'status': 500, 'error': 'no items found in payload' }
    if 'id_field' not in payload:
        return { 'status': 500, 'error': 'no id_field found in payload' }
    if 'geocode_query_field' not in payload:
        return { 'status': 500, 'error': 'no geocode_query_field found in payload' }
    items = payload['items']
    id_field = payload['id_field']
    query_field = payload['geocode_query_field']

    # get all the geocodes for all the items
    _, new_geocodes = items_geocode(items, id_field, query_field)

    # filter failed rows
    new_table_rows = [dict(query=urllib.parse.unquote(k), geo=v) for k, v in new_geocodes.items()]
    for r in new_table_rows:
        r['geo'] = list(filter(lambda x: 'parsing_failed' not in x, r['geo']))
    new_table_rows = list(filter(lambda x: len(x['geo']) != 0, new_table_rows))

    # update dynamo table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('geocode')
    put_items(table, new_table_rows)

    return { 'status': 200 }
