import unittest
from mock import Mock, patch, MagicMock
from app.external.companies import (get_name_from_symbol, get_symbol_lists,
                                    get_sector_and_industry, g_get_sector_and_industry, y_get_sector_and_industry
                                    )


class TestCompanyExternal(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_name_from_symbol(self):
        # valid company name
        with patch("requests.get") as my_mock:
            m2 = MagicMock()
            m2.json.return_value = {'result': {'rows': [{'values': [{'field': 'companyname', 'value': 'Microsoft'}]}]}}
            my_mock.return_value = m2
            self.assertEqual(get_name_from_symbol("MSFT"), "Microsoft")

        ## invalid symbol
        with patch("requests.get") as my_mock:
            m2 = MagicMock()
            m2.json.return_value = {'result': {'rows': [{'values': [{'field': 'companyname', 'value': 'Microsoft'}]}]}}
            my_mock.return_value = m2
            self.assertEqual(get_name_from_symbol("ZZZZ123"), None)

        ## throw exception
        with patch("requests.get") as my_mock:
            my_mock.r.json.side_effect = KeyError
            self.assertEqual(get_name_from_symbol("MSFT"), None)

    def test_get_symbol_lists(self):
        r = get_symbol_lists()
        self.assertEqual(r.status_code, 200)
        r = get_symbol_lists(index="NASDAQ")
        self.assertEqual(r.status_code, 200)

    def test_get_sector_and_industry(self):
        self.assertEqual(get_sector_and_industry('aapl'), {'industry': u'Computer Hardware - NEC', 'sector': u'Technology'})

    def test_g_get_sector_and_industry(self):
        self.assertEqual(g_get_sector_and_industry('aapl'), {'industry': u'Computer Hardware - NEC', 'sector': u'Technology'})

    def test_y_get_sector_and_industry(self):
        self.assertEqual(y_get_sector_and_industry('aapl'), {'industry': u'Electronic Equipment', 'sector': u'Consumer Goods'})
