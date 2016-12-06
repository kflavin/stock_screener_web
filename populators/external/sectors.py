import re
import requests
from bs4 import BeautifulSoup
import logging
from selenium.webdriver import PhantomJS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib2 import URLError

logger = logging.getLogger('populators.external.sectors')


def get_sector_and_industry(symbol):
    """
    Makes two calls for redundancy...  Note that g_ and y_ are not compatible
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
