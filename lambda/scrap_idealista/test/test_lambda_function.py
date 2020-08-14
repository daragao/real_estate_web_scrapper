import lambda_function as lf
import scrap_idealista as si
import unittest
import os
import responses
from decimal import Decimal

def local_path(filename):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(__location__, filename)

class TestLambdaFunction(unittest.TestCase):

    def setUp(self):
        pass

    @responses.activate
    def test_scanned_id(self):

        req_urls = [
            "https://www.idealista.pt/en/comprar-casas/lisboa/com-tamanho-min_100,publicado_ultimas-48-horas",
            "https://www.idealista.pt/en/comprar-casas/lisboa/com-tamanho-min_100,publicado_ultimas-48-horas/pagina-2",
            "https://www.idealista.pt/en/comprar-casas/lisboa/com-tamanho-min_100,publicado_ultimas-48-horas/pagina-3",
            "https://www.idealista.pt/en/comprar-casas/lisboa/com-tamanho-min_100,publicado_ultimas-48-horas/pagina-4",
            "https://www.idealista.pt/en/comprar-casas/lisboa/com-tamanho-min_100,publicado_ultimas-48-horas/pagina-5"
        ]
        for i in range(1,6):
            f = open(local_path('dummy_page_{}.html'.format(i)), "rb")
            content = f.read().decode(encoding="utf-8")
            f.close()
            responses.add(responses.GET, req_urls[i-1], body=content, status=200)

        items = {
            '00000001': { # same price as scanned item (it can be dropped)
                'address': 'Parque%20das%20Na%C3%A7%C3%B5es%2C%20Lisboa',
                'url': 'https://www.idealista.pt/en/imovel/30653248/',
                'price': 650000, 'id': '00000001', 'size': 141, 'created': '14-08-2020 22:49:16'
            },
            '00000002': {
                'address': 'Olivais%2C%20Lisboa',
                'url': 'https://www.idealista.pt/en/imovel/30656463/',
                'price': 598000, 'id': '00000002', 'size': 612, 'created': '14-08-2020 22:49:16'
            },
            '00000003': {
                'address': 'rua%20Coelho%20da%20Rocha%2C%2095%2C%20Campo%20de%20Ourique%2C%20Lisboa',
                'url': 'https://www.idealista.pt/en/imovel/30652632/',
                'price': 589900, 'id': '00000003', 'size': 135, 'created': '14-08-2020 22:49:16'
            },
            '00000004': {
                'address': 'Centro%20-%20Nova%20Campolide%2C%20Campolide',
                'url': 'https://www.idealista.pt/en/imovel/30624477/',
                'price': 780000, 'id': '00000004', 'size': 104, 'created': '14-08-2020 22:49:16'
            },
            '00000005': {
                'address': 'Centro%20-%20Nova%20Campolide%2C%20Campolide',
                'url': 'https://www.idealista.pt/en/imovel/30624484/',
                'price': 1370000, 'id': '00000005', 'size': 204, 'created': '14-08-2020 22:49:16'
            },
            '00000006': { # no matching scanned item, but new (so can't be dropped)
                'address': 'Areeiro%2C%20Lisboa',
                'url': 'https://www.idealista.pt/en/imovel/30652463/',
                'price': 490000, 'id': '00000006', 'size': 107, 'created': '14-08-2020 22:49:16'
            }
        }
        scanned_items = {
            '00000001': {'created': '12-08-2020 23:00:49', 'id': '00000001', 'price': Decimal('650000')}, # same price as scanned item (it can be dropped)
            '00000002': {'created': '12-08-2020 23:00:49', 'id': '00000002', 'price': Decimal('1370000')},
            '00000003': {'created': '12-08-2020 23:00:49', 'id': '00000003', 'price': Decimal('780000')},
            '00000004': {'created': '12-08-2020 23:00:50', 'id': '00000004', 'price': Decimal('490000')},
            '00000005': {'created': '13-08-2020 23:00:51', 'id': '00000005', 'price': Decimal('650000')},
            '00000000': {'created': '14-08-2020 17:07:15', 'id': '00000000', 'price': Decimal('598000')} # no matching item
        }

        new_items = lf.add_updated_columns(items.values(), scanned_items.values())
        self.assertEqual(len(items)-1, len(new_items))

        scanned_ids = scanned_items.keys()
        for it in new_items:
            if it['id'] in scanned_ids:
                self.assertIn('price_update', it)
                self.assertIn('date_update', it)

                self.assertEqual(len(it['price_update']), 2)
                self.assertNotEqual(float(it['price']), float(scanned_items[it['id']]['price']))
                for price in it['price_update']:
                    self.assertIsInstance(price, Decimal)
            else:
                self.assertNotIn('price_update', it)
                self.assertNotIn('date_update', it)
                self.assertEqual(it['id'], '00000006') # this is the only item that does not need updating and remains in items because it is new
