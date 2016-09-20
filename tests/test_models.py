import unittest
from flask import current_app
from app import create_app, db
from app.models import Company, Indicators


class TestCompany(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Company.generate_fake(10)
        Indicators.generate_fake(3)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_companies_created(self):
        companies = Company.query.count()
        self.assertTrue(companies != 0)

    def test_validate_symbol(self):
        self.assertTrue(Company.validate_symbol("GOOD"))
        self.assertFalse(Company.validate_symbol("Bad"))

    def test_validate_name(self):
        self.assertTrue(Company.validate_name("Good Company"))
        self.assertFalse(Company.validate_name("Bad Company**!"))

    def test_from_json(self):
        c = Company.from_json({'name': 'ABC Company', 'symbol': 'ABC'})
        self.assertTrue(isinstance(c, Company))
        with self.assertRaises(ValueError):
            c = Company.from_json({'name': '', 'symbol': ''})
