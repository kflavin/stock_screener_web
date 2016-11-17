import unittest

from datetime import date
from mock import Mock, patch, MagicMock
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

    def test_company_from_json(self):
        c = Company.from_json({'name': 'ABC Company', 'symbol': 'ABC', 'index': "NYSE"})
        self.assertTrue(isinstance(c, Company))
        with self.assertRaises(ValueError):
            c = Company.from_json({'name': '', 'symbol': ''})

        c = Company.from_json({'name': 'DEF Company', 'symbol': 'DEF', 'active': False})
        self.assertTrue(isinstance(c, Company))


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Company.generate_fake(10)
        Indicators.generate_fake(4)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_indicators_from_json(self):
        # Create new company
        symbol = "ZZZZZ"
        name = "Fake Name"
        d = {'symbol': symbol, "roe": 0.25, "fcf": 100.0, "name": name}
        Indicators.from_json(d)
        c = Company.query.filter_by(symbol=symbol)
        self.assertIsNotNone(c)
        # use existing company
        d = {"roe": 0.25, "fcf": 100.0}
        Indicators.from_json(d)

    def test_equal_values(self):
        # same indicators should return equal
        i1 = Company.query.first().indicators.first()
        i2 = Company.query.first().indicators.first()
        self.assertTrue(Indicators.equal_values(i1, i2))

        # Indicators with different values (excluding date) are not equal
        i1 = Indicators(date=date.today(), roe=1.1, fcf=2.2, ev2ebitda=3.3)
        i1.company = Company.query.first()
        i2 = Indicators(date=date.today(), roe=2.2, fcf=1.1, ev2ebitda=4.4)
        i2.company = Company.query.first()
        self.assertFalse(Indicators.equal_values(i1, i2))




