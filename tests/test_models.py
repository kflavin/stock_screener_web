import unittest

from datetime import date, timedelta
from mock import Mock, patch, MagicMock
from flask import current_app
from app import create_app, db
from app.models import Company, Indicators


class TestCompany(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        print "your db is", db
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
        c = Company.from_json({'name': 'ABC Company', 'symbol': 'ABC', 'exchange': "NYSE"})
        self.assertTrue(isinstance(c, Company))
        with self.assertRaises(ValueError):
            c = Company.from_json({'name': '', 'symbol': ''})

        c = Company.from_json({'name': 'DEF Company', 'symbol': 'DEF', 'active': False})
        self.assertTrue(isinstance(c, Company))

    def test_update_company(self):
        company = Company.query.first()
        symbol = company.symbol

        d = {'name': 'New Company', 'symbol': symbol, 'sector': "BOGUSSECTOR", 'industry': "BOGUSINDUSTRY"}
        Company.update(d)
        company = Company.query.filter(Company.symbol == symbol).first()
        self.assertEqual(company.name, "New Company")
        self.assertEqual(company.sector, "BOGUSSECTOR")
        self.assertEqual(company.industry, "BOGUSINDUSTRY")


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Company.generate_fake(10)
        Indicators.generate_fake(4)

        # l = self.company.indicators.all()
        # l = sorted(l, key=lambda k: getattr(k, 'date'))
        # i = l.pop()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_indicators_from_json(self):
        # Create new company
        # l = self.company.indicators.all()
        # l = sorted(l, key=lambda k: getattr(k, 'date'))
        # i = l.pop()
        symbol = "ZZZZZ"
        name = "Fake Name"
        d = {'symbol': symbol, "roe": 0.25, "fcf": 100.0, "name": name}
        Indicators.from_json(d)
        c = Company.query.filter_by(symbol=symbol)
        self.assertIsNotNone(c, "Company should exist after json is loaded.")
        # use existing company
        d = {"roe": 0.25, "fcf": 100.0}
        try:
            Indicators.from_json(d)
        except Exception as e:
            self.fail("Raised {}".format(e))

    # def test_equal_values(self):
    #     # same indicators should return equal
    #     i1 = Company.query.first().indicators.first()
    #     i2 = Company.query.first().indicators.first()
    #     self.assertTrue(Indicators.equal_values(i1, i2))
    #
    #     # Indicators with different values (excluding date) are not equal
    #     i1 = Indicators(date=date.today(), roe=1.1, fcf=2.2, ev2ebitda=3.3)
    #     i1.company = Company.query.first()
    #     i2 = Indicators(date=date.today(), roe=2.2, fcf=1.1, ev2ebitda=4.4)
    #     i2.company = Company.query.first()
    #     self.assertFalse(Indicators.equal_values(i1, i2))

    @staticmethod
    def create_duplicate(indicator=None):
        if not indicator:
            company = Company.query.first()
            indicator = sorted(company.indicators.all(), key=lambda k: getattr(k, 'date')).pop()
        i1 = Indicators()
        i1.company = indicator.company
        # i2 = Indicators()
        # i2.company_id = company.id

        # Grab the first indicator, and make two duplicates
        for column in Indicators.__table__.columns.keys():
            if column not in Indicators.ignore_attrs:
                setattr(i1, column, getattr(indicator, column))
                # setattr(i2, column, getattr(indicator, column))

        return i1

    def test_is_duplicate_of_last(self):
        i1 = self.create_duplicate()
        i1.date += timedelta(days=1)
        self.assertEqual(i1.is_duplicate_of_last(), True, "i1 should be reported as a duplicate indicator")

    def test__eq__(self):
        """
        Checking for duplicates in different ways

        Returns:

        """
        i1 = self.create_duplicate()
        i2 = self.create_duplicate(i1)
        i2.ev2ebitda += 1
        self.assertEqual(i1, i2, "Companies should be equal, but are being reported as not.")

        i2.fcf += 1
        self.assertNotEqual(i1, i2, "Companies should NOT be equal, but are being reported as equal.")

        db.session.rollback()

        # same indicators should return equal
        i1 = Company.query.first().indicators.first()
        i2 = Company.query.first().indicators.first()
        self.assertTrue(i1 == i2, "The same indicator should be equal to itself")

        # Indicators with different values (excluding date) are not equal
        i1 = Indicators(date=date.today(), roe=1.1, fcf=2.2, ev2ebitda=3.3)
        i1.company = Company.query.first()
        i2 = Indicators(date=date.today(), roe=2.2, fcf=1.1, ev2ebitda=4.4)
        i2.company = Company.query.first()
        self.assertFalse(i1 == i2, "Indicators with differing fcf and roe should return equal regardless of date")



