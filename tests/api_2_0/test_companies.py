from app import db
from app.models import Company, Indicators
from base import BaseTest
import json


class TestCompany(BaseTest):

    def setUp(self):
        #BaseTest.setUp(self)
        super(TestCompany, self).setUp()

        Company.generate_fake(10)
        Indicators.generate_fake(3)

    def test_get_companies(self):
        # Logged in
        token = self.get_token()

        with self.client:
            headers = {
                'Authorization': 'Bearer ' + token
            }
            response = self.client.get(
                '/api/2.0/company/',
                headers=headers,
                content_type="application/json"
            )

            data = json.loads(response.data.decode())
            self.assertGreater(data.get('total'), 1)
            self.assertIsNotNone(data.get('companies'))
            self.assertEqual(response.status_code, 200)

