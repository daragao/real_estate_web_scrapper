import scrap_idealista as si
import unittest
import os
import responses

def local_path(filename):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(__location__, filename)

class TestScrapIdealista(unittest.TestCase):

    def setUp(self):
        pass

    @responses.activate
    def test_scrap(self):

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

        items = si.scrap()

        for it in items:
            self.assertIn('price', it)
            self.assertIn('address', it)
            self.assertIn('id', it)
            self.assertIn('size', it)
            self.assertIn('url', it)
            self.assertIn('created', it)
        self.assertEqual(len(items), 133)

    @responses.activate
    def test_scrap_400(self):

        req_urls = [
            "https://www.idealista.pt/en/comprar-casas/lisboa/com-tamanho-min_100,publicado_ultimas-48-horas",
            "https://www.idealista.pt/en/comprar-casas/lisboa/com-tamanho-min_100,publicado_ultimas-48-horas/pagina-2",
            "https://www.idealista.pt/en/comprar-casas/lisboa/com-tamanho-min_100,publicado_ultimas-48-horas/pagina-3",
        ]
        for i in range(1,3):
            f = open(local_path('dummy_page_{}.html'.format(i)), "rb")
            content = f.read().decode(encoding="utf-8")
            f.close()
            responses.add(responses.GET, req_urls[i-1], body=content, status=200)
        responses.add(responses.GET, req_urls[2], body="Breaking bad", status=400)

        items = si.scrap()

        for it in items:
            self.assertIn('price', it)
            self.assertIn('address', it)
            self.assertIn('id', it)
            self.assertIn('size', it)
            self.assertIn('url', it)
            self.assertIn('created', it)
        self.assertEqual(len(items), 60)
