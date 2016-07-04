import unittest
from flask import current_app
from app import create_app, db
from app.models import Company


class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Company.generate_fake(100)
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_companies_created(self):
        companies = Company.query.count()
        self.assertTrue(companies != 0)
