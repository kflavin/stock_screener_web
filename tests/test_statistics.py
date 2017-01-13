import unittest
from app import create_app, db
from app.main.statistics import get_averages

from base import load_fixtures


class TestStatistics(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        load_fixtures()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_averages(self):
        sector_averages = get_averages("sector", "Industrials")

        self.assertEqual(sector_averages.get('roe'), 6.8575, "ROE doesn't match")
        self.assertEqual(sector_averages.get('fcf'), 553815000.5, "FCF doesn't match")
        self.assertEqual(sector_averages.get('ev2ebitda'), 11.04, "EV2EBITDA doesn't match")

        industry_averages = get_averages("industry", "Industrials")
        self.assertEqual(industry_averages.get('roe'), 6.8575, "ROE doesn't match")
        self.assertEqual(industry_averages.get('fcf'), 553815000.5, "FCF doesn't match")
        self.assertEqual(industry_averages.get('ev2ebitda'), 11.04, "EV2EBITDA doesn't match")
