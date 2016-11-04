import unittest
from mock import Mock, patch, MagicMock
from app.external.companies import get_name_from_symbol


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
