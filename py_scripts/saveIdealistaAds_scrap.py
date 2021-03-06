import requests
from bs4 import BeautifulSoup
import textwrap
from datetime import datetime
import json
import urllib

########################
# Load setup details (cookie)
########################
with open("scrap.json") as json_file:
    scrap_json = json.load(json_file)
print('Loaded scrap json:\n\tUID: {}'.format(scrap_json['uid']))

def json_to_cookie(cookie_json):
    return '; '.join(['{}={}'.format(k,v) for k, v in cookie_json.items()])

########################
# HTTP Request data
########################
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'cookie': json_to_cookie(scrap_json['cookie'])
}

articles = []

host = 'https://www.idealista.pt'
path = 'en/comprar-casas'
region = 'lisboa'
params = ['com-tamanho-min_100','publicado_ultimas-48-horas']
url = '/' + '/'.join([path,region,','.join(params)])

i = 0
while url:
    i += 1
    url = host + url
    print('{}) Request URL: {}'.format(i, url))

    req = requests.get(url, headers)
    if(req.status_code != 200):
        print('{}) HTTP Code {}\n\tBody: {}'.format(i, req.status_code,req.text))
        break

    soup = BeautifulSoup(req.content, 'html.parser')

    articles += soup.find_all('article')

    print('\tArticles/Ads found: {}'.format(len(articles)))
    pagination = soup.find('div', 'pagination')

    next_page_tag = pagination.find('a', 'icon-arrow-right-after')
    url = next_page_tag.get('href') if next_page_tag else None

########################
# Parse HTML
########################
items = []
for ad in articles:
    # .info-data-price
    if('adv' in ad.attrs['class']):
        continue
    item_price = ad.find('span', class_='item-price')
    item_detail = ad.find_all('span', class_='item-detail')
    item_link = ad.find('a', class_='item-link')
    item_title = item_link.get('title')
    item_id = ad.get('data-adid')

    price = int(item_price.get_text()[:-1].replace(',',''))
    address = urllib.parse.quote(item_title[item_title.find(' in ')+4:]) if item_title.find(' in ') != - 1 else item_title
    size = int(item_detail[1].get_text()[:-3].replace(',','')) if len(item_detail) > 1 else print('{} Failed to fetch area!'.format(item_id))
    item_url = '{}{}'.format(host,item_link.get('href'))

    items.append({
        'price': price,
        'address': address,
        'id': item_id,
        'size': size,
        'url': item_url,
        'created': datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    })
    #print(json.dumps(items_dict[item_id], indent=4, sort_keys=True))
print('Ads parsed: {}'.format(len(items)))


########################
# Save file
########################
time_format = '%d-%m-%Y_%H:%M:%S_scrap'
data_path = './data_scrap'

now = datetime.now()
s2 = now.strftime(time_format)

f = open(data_path + '/' + s2 + ".json","w")
f.write(json.dumps(items))
f.close()
