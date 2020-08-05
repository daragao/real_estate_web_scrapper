import requests
from bs4 import BeautifulSoup
import textwrap
from datetime import datetime
import json
import urllib
from decimal import Decimal
from re import sub

def get_imovirtual_articles(url):
    total_pages = 0
    articles = []
    while(url):
        print('Request URL: {}'.format(url))
        total_pages += 1
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')
        articles += soup.find_all('article')

        pagination = soup.find('li', 'pager-next')
        next_page_tag = pagination.find('a')
        url = next_page_tag.get('href') if next_page_tag else None
    return articles, total_pages

def imovirtual_article_to_json(art):
    offer_details = art.find('div', 'offer-item-details')

    price_el = offer_details.find('li','offer-item-price')
    size_el = offer_details.find('li','offer-item-area')
    price_str = sub(r'[^\d.,]', '', price_el.get_text())
    size_str = sub(r'[^\d.,]', '', size_el.get_text()).replace(',','.')
    if(len(price_str) == 0): price_str = None

    title = art.find('header', 'offer-item-header').find('span', 'offer-item-title').get_text().strip()
    address = offer_details.find('p').find('span').next_sibling
    size = Decimal(size_str)
    price = Decimal(price_str) if price_str != None else None
    advertising_link = art.get('data-url')
    data_id = art.get('data-item-id')
    tracking_id = art.get('data-tracking-id')
    offer_dict = {
        'title': title,
        'price': price,
        'url': advertising_link,
        'item-id': data_id,
        'tracking-id': tracking_id,
        'size': size,
        'address': address,
        'price_note': None if price != None else price_el.get_text().strip(),
        'created': datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    }

    return offer_dict

def scrap_imovirtual():
    host = 'https://www.imovirtual.com'
    path = 'comprar/apartamento/lisboa'
    query_dict = {
        "search[created_since]": "3",
        "search[filter_float_m:from]": "100",
        "search[region_id]": "11",
        "search[subregion_id]": "153"
    }
    query = urllib.parse.urlencode(query_dict)

    url = '{}/{}/?{}'.format(host,path,query)

    articles, total_pages = get_imovirtual_articles(url)
    print('Total pages: {}\nTotal articles: {}'.format(total_pages,len(articles)))

    items = []
    for art in articles:
        items.append(imovirtual_article_to_json(art))
    return items
