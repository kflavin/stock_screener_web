import unittest
from mock import patch
from app import create_app, db
from app.models import Company
#import populate_companies
from populate_companies import get_company_details


class TestPopulateCompanies(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        get_company_details(count=2)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_company_details(self):
        self.assertEqual(2, Company.query.count())

