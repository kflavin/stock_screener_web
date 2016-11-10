import unittest
from mock import patch
from app import create_app, db
from app.models import Company, Indicators
from populate_companies import get_company_details
from populate_indicators import get_ratio_data


class TestPopulateIndicators(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_company_details(self):
        get_company_details(count=2)
        get_ratio_data()
        self.assertEqual(Company.query.count(), Company.query.join(Indicators).count())


