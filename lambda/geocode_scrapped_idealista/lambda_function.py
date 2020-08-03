import json
import geocode
import boto3

def lambda_handler(event, context):
    items = event['responsePayload']['items']
    print('Received event: {}'.format(event))
    geocode.geocode(items)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('scrapped_ads')
    # overwrites old values
    # TODO: have an array of changed values
    with table.batch_writer() as batch:
        for it in items:
            batch.put_item(Item=it)

    return {
        'statusCode': 200,
        'items-len': len(items),
        'body': json.dumps('Hello from Lambda!')
    }
