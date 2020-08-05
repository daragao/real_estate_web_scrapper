import scrapper_imovirtual as scrapper
import json

def lambda_handler(event, context):
    print('Received event: {}'.format(event))

    items = scrapper.scrap_imovirtual()

    return { 'status': 200, 'items': items }
