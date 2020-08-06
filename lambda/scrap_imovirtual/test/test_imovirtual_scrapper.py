import scrapper_imovirtual as scrapper
import lambda_function
import unittest
from unittest.mock import Mock, patch

import urllib
import json
from decimal import Decimal
import os

from bs4 import BeautifulSoup
import responses

def local_path(filename):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(__location__, filename)

class TestScrapperImovirtual(unittest.TestCase):

    def setUp(self):
        f = open(local_path('dummy_page.html'), "r")
        page_1 = f.read()
        f.close()
        f = open(local_path('dummy_page_2.html'), "r")
        page_2 = f.read()
        f.close()

        host = 'https://www.imovirtual.com/comprar/apartamento/lisboa/?'
        path_1 = 'search%5Bcreated_since%5D=3&search%5Bfilter_float_m%3Afrom%5D=100&search%5Bregion_id%5D=11&search%5Bsubregion_id%5D=153'
        path_2 = 'search%5Bcreated_since%5D=3&search%5Bfilter_float_m%3Afrom%5D=100&search%5Bregion_id%5D=11&search%5Bsubregion_id%5D=153&page=2'

        responses.add(responses.GET, host+path_1, body=page_1, status=200)
        responses.add(responses.GET, host+path_2, body=page_2, status=200)

    @responses.activate
    def test_get_imovirtual_articles(self):
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

        articles, total_pages = scrapper.get_imovirtual_articles(url)
        self.assertGreater(total_pages, 0)

    def test_imovirtual_article_to_json(self):
        with open(local_path('dummy_articles.json')) as json_file:
            json_data = json.load(json_file)
            art = BeautifulSoup(json_data[0], 'html.parser').find('article')


        art_dict = scrapper.imovirtual_article_to_json(art)
        self.assertEqual(art_dict["address"], "Avenidas Novas, Lisboa")
        #self.assertEqual(art_dict["created"], "05-08-2020 21:30:05")
        self.assertEqual(art_dict["item-id"], "13AlZ")
        self.assertEqual(art_dict["price"], 1320000.0)
        self.assertEqual(art_dict["price_note"], None)
        self.assertEqual(art_dict["size"], 145.0)
        self.assertEqual(art_dict["title"], "Oasis 28. T3 com terra\u00e7o 42 m2, 2 estacionamentos e arrec...")
        self.assertEqual(art_dict["tracking-id"], "15631067")
        self.assertEqual(art_dict["url"], "https://www.imovirtual.com/anuncio/oasis-28-t3-com-terraco-42-m2-2-estacionamentos-e-arrec-ID13AlZ.html#22dd3644e3")

    @responses.activate
    def test_scrap_imovirtual(self):
        items = scrapper.scrap_imovirtual()
        self.assertEqual(len(items), 48)

    @unittest.skip("NEED TO MOCK AWS BOTO3")
    @responses.activate
    def test_lambda_function(self):
        #lambda_function.lambda_handler({ 'test': 'hello' }, None)
        pass
