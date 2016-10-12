import unittest
from app.utils import cash_to_float, depercentize


class TestUtils(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cash_to_float(self):
        self.assertEqual(cash_to_float(1.0), 1.00)
        self.assertEqual(cash_to_float("1.0M"), 1000000.0)
        self.assertEqual(cash_to_float("231.231k"), 231231.0)
        self.assertEqual(cash_to_float("15R"), 0.0)
        self.assertEqual(cash_to_float("R15"), 0.0)
        self.assertEqual(cash_to_float("garbage"), 0.0)

    def test_depercentize(self):
        self.assertEqual(depercentize("22.3%"), 22.3)
        self.assertEqual(depercentize(None), 0.0)
        self.assertEqual(depercentize("invalid"), 0.0)
        self.assertEqual(depercentize(-12.5), -12.5)
        self.assertEqual(depercentize("-12.5"), -12.5)

