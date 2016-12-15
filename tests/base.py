import unittest
import os
import datetime
from app import create_app, db
from app.models import Company, Indicators, User
from populators.companies import get_company_details

email=os.environ.get('CLI_USER') or 'testuser'
password=os.environ.get('CLI_PASSWORD') or 'password'


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        db.session.add(User(email=email, password=password, active=True, confirmed_at=datetime.datetime.utcnow()))
        db.session.commit()

        self.client = self.app.test_client()
        self.login(email, password)

        r = self.client.get('/api/1.0/company/', follow_redirects=True)

        self.count = 10
        Company.generate_fake(self.count)
        Indicators.generate_fake(2)

        # get_company_details(count=2, user=email, password=password)
        # get_ratio_data(user=email, password=password)

    def login(self, email, password):
        return self.client.post('/login', data=dict(
                email=email,
                password=password
            ), follow_redirects=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


if __name__ == '__main__':
    unittest.main()
