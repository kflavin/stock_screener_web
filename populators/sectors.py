import os
import logging
import requests
from requests.auth import HTTPBasicAuth

from populators.external.companies import get_sector_and_industry

logger = logging.getLogger('populators.sectors')


def get_sectors_and_industries(count=None):
    host = os.environ.get('CLI_HOST')
    user = os.environ.get('CLI_USER')
    password = os.environ.get('CLI_PASSWORD')

    auth = HTTPBasicAuth(user, password)

    if count:
        r = requests.get("http://{}/api/1.0/company/?count={}".format(host, count), auth=auth)
    else:
        print "get sector and industry "
        total = requests.get("http://{}/api/1.0/company/".format(host), auth=auth).json().get('total')
        r = requests.get("http://{}/api/1.0/company/?count={}".format(host, total), auth=auth)

    companies = r.json().get('companies')

    logger.info("Getting data for {} companies".format(len(companies)))
    for company in companies:
        symbol = company.get('symbol')
        sector_and_industry = get_sector_and_industry(symbol)
        print sector_and_industry, symbol
        r = requests.post("http://{}/api/1.0/company/{}".format(host, symbol), json=sector_and_industry, auth=auth)

