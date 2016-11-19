import requests
import re
import sys
from bs4 import BeautifulSoup
import logging
from selenium.webdriver import PhantomJS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib2 import URLError

logger = logging.getLogger('app.external.companies')


def get_name_from_symbol(symbol):
    """
    Use EDGAR online database to find the company name.
    """
    from flask import current_app
    import dryscrape
    from app.models import Company

    if not Company.validate_symbol(symbol):
        return None

    r = requests.get("http://edgaronline.api.mashery.com/v2/companies?primarysymbols={}&appkey={}".format(symbol, current_app.config['EDGAR_APP_KEY']))

    try:
        values = r.json()['result']['rows'][0]['values']
    except (KeyError, IndexError) as e:
        return None

    companyname = None
    for value in values:
        if value.get('field') == "companyname":
            companyname = value.get('value')
            break

    return companyname


def get_symbol_lists(index='NYSE', page="A"):
    """
    index: NYSE or NASDAQ
    """
    return requests.get("http://eoddata.com/stocklist/{}/{}.htm".format(index, page))


def get_sic_code(symbol):
    r = requests.get(
        "https://www.sec.gov/cgi-bin/browse-edgar?CIK={}&owner=exclude&action=getcompany&Find=Search".format(symbol))
    soup = BeautifulSoup(r.text, "lxml")
    regex = re.compile(".*SIC=(\d+)")
    try:
        a_href = soup.find('acronym', attrs={'title': 'Standard Industrial Code'}).find_next_sibling('a', attrs={
            'href': regex}).attrs['href']
    except AttributeError:
        logger.warning("Could not get sic code for {}".format(symbol))
        return None

    match = re.match(regex, a_href)
    if match:
        return match.groups()[0]


def get_sector_and_industry(symbol):
    """
    Makes two calls for redundancy...
    Args:
        symbol:

    Returns:

    """
    return g_get_sector_and_industry(symbol)


def g_get_sector_and_industry(symbol):
    r = requests.get("https://www.google.com/finance?q={}".format(symbol.lower()))
    soup = BeautifulSoup(r.text, "lxml")
    try:
        sector = soup.find("a", attrs={'id': 'sector'}).text
        industry = soup.find("a", attrs={'id': 'sector'}).find_next_sibling('a').text
    except AttributeError:
        return None

    return {'sector': sector, 'industry': industry}


def y_get_sector_and_industry(symbol):
    """
    Potential fallback, unused currently.
    Args:
        symbol: company symbol

    Returns: Dict of sector and industry

    """

    classifications = {
        'sector': {
            'tag': 'strong',
            'attribute': 'data-reactid',
            'value': re.compile(".*\$asset-profile\.1\.1\.1\.2$"),
        },
        'industry': {
            'tag': 'strong',
            'attribute': 'data-reactid',
            'value': re.compile(".*\$asset-profile\.1\.1\.1\.6$"),
        },
    }

    try:
        driver = PhantomJS()
    except URLError:
        return None

    driver.set_window_size(1120, 550)
    driver.get("http://finance.yahoo.com/quote/{}/profile?p={}".format(symbol.upper(), symbol.upper()))

    try:
        # Wait until we see this element before continuing
        element = WebDriverWait(driver, 10).\
            until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[substring(@data-reactid, string-length(@data-reactid) - string-length('$asset-profile.1.1.1.6') +1) = '$asset-profile.1.1.1.6']")
            )
        )
    except TimeoutException as e:
        print "Caught", e
        print driver.title
        return None

    soup = BeautifulSoup(driver.page_source, "lxml")

    d = {}
    logger.debug("Checking {}".format(symbol))
    for c in classifications.keys():
        curr_c = classifications[c]
        s = soup.find(curr_c['tag'], attrs={curr_c['attribute']: curr_c['value']}).text
        logger.info("{} found {}".format(c, s))
        d[c] = s

    return d