from base import BaseTest
from app.models import Company


class TestPopulateCompanies(BaseTest):
    def test_get_company_details(self):
        self.assertGreaterEqual(Company.query.count(), 1, "Failed to add at least one Company")

