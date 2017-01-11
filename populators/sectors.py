import os
import logging
import requests
from requests.auth import HTTPBasicAuth

from populators.external.companies import get_sector_and_industry

logger = logging.getLogger('populators.sectors')


def get_sectors_and_industries(count=None, host="http://localhost:5000", user="user", password="password"):

    auth = HTTPBasicAuth(user, password)

    if count:
        r = requests.get("{}/api/1.0/company/?count={}".format(host, count), auth=auth)
    else:
        print "get sector and industry "
        try:
            total = requests.get("{}/api/1.0/company/".format(host), auth=auth).json().get('total')
        except ValueError:
            print "Unauthorized access.  Cannot retrieve company data"
            return
        r = requests.get("{}/api/1.0/company/?count={}".format(host, total), auth=auth)


    companies = sorted(r.json().get('companies'), key=lambda x: x['symbol'])

    logger.info("Getting data for {} companies".format(len(companies)))
    for company in companies:
        symbol = company.get('symbol')
        sector_and_industry = get_sector_and_industry(symbol)
        print sector_and_industry, symbol
        r = requests.post("{}/api/1.0/company/{}".format(host, symbol), json=sector_and_industry, auth=auth)

        if r.status_code == 201:
            print "success"
        else:
            print "Failed with", r.status_code

