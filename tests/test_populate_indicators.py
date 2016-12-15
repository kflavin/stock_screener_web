import unittest
import os
from base import BaseTest
from app.models import Company, Indicators, User


class TestPopulateIndicators(BaseTest):
    def test_get_company_details(self):
        self.assertEqual(Company.query.count(), Company.query.join(Indicators).count(), "Indicator count should match Companies")


if __name__ == '__main__':
    unittest.main()