import unittest
from app.utils import cash_to_float, depercentize, get_industry
from lib.siccodes import codes


class TestUtils(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cash_to_float(self):
        asdf
        self.assertEqual(cash_to_float(1.0), 1.00)
        self.assertEqual(cash_to_float("1.0M"), 1000000.0)
        self.assertEqual(cash_to_float("231.231k"), 231231.0)
        self.assertEqual(cash_to_float("15R"), None)
        self.assertEqual(cash_to_float("R15"), None)
        self.assertEqual(cash_to_float("garbage"), None)

    def test_depercentize(self):
        self.assertEqual(depercentize("22.3%"), 22.3)
        self.assertEqual(depercentize(None), None)
        self.assertEqual(depercentize("invalid"), None)
        self.assertEqual(depercentize(-12.5), None)
        self.assertEqual(depercentize("-12.5"), -12.5)

    def test_get_industry(self):
        self.assertEqual('Electronic Computers', get_industry(3571))
        self.assertEqual('Electronic Computers', get_industry('3571'))

