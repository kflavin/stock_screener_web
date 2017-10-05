import os
import logging
import requests
from requests.auth import HTTPBasicAuth

from populators.external.companies import get_sector_and_industry

logger = logging.getLogger('populators.sectors')
# logger = logging.getLogger(__name__)


def get_sectors_and_industries(count=None,
                               host="http://localhost:5000",
                               user="user", password="password",
                               empty_only=True,
                               api_url="api/2.0"):

    logger.debug("count: {}, host: {}, user: {}, empty_only: {}".format(count, host, user, empty_only))
    auth = HTTPBasicAuth(user, password)
    url = "{}/{}/company/".format(host, api_url)

    if count:
        r = requests.get("{}?count={}&empty_only={}".format(url, count, empty_only), auth=auth)
    else:
        try:
            total = requests.get("{}?empty_only={}".format(url, empty_only), auth=auth).json().get('total')
            logger.info("Retrieved {} companies".format(total))
        except ValueError:
            logger.error("Unauthorized access.  Cannot retrieve company data")
            return
        r = requests.get("{}?count={}&empty_only={}".format(url, total, empty_only), auth=auth)

    companies = sorted(r.json().get('companies'), key=lambda x: x['symbol'])

    logger.debug("Getting data for {} companies".format(len(companies)))
    for company in companies:
        symbol = company.get('symbol')
        sector_and_industry = get_sector_and_industry(symbol)
        if sector_and_industry:
            r = requests.post("{}{}".format(url, symbol), json=sector_and_industry, auth=auth)

            if r.status_code == 201:
                print "Added", company.get('symbol')
            else:
                print "Failed with", r.status_code
                logger.debug(r.text)

