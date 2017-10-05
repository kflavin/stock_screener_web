import sys
from selenium.webdriver import PhantomJS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
from requests.auth import HTTPBasicAuth
from urllib2 import URLError
# from app import db


# class MyWebDriver(PhantomJS):
#     def __init__(self, *a, **kw):
#         super(MyWebDriver, self).__init__(*a, **kw)
#         self._maxRequestCount = 100
#         self._RequestCount = 0
#
#     def get(self, url):
#         if self._RequestCount > self._maxRequestCount:
#             self.__reset()
#         super(MyWebDriver, self).get(url)
#         self._RequestCount += 1
#
#     def __reset(self):
#         try:
#             self.quit()
#         except:
#             print("couldn't quit, do so manually")
#         self.__dict__ = self.__class__().__dict__

api_url = "/api/2.0"  # no trailing backslash
yahoo_url = "http://finance.yahoo.com/quote/{}/key-statistics?p={}"

def get_ratio_data(count=None, host="http://127.0.0.1:5000", user="user", password="password"):
    import re
    import time
    import os
    from bs4 import BeautifulSoup

    # from app.models import Company, Indicators
    from app.utils import cash_to_float, depercentize

    auth = HTTPBasicAuth(user, password)


    # Dict item with list: element attribute, attribute value to look for, optional transform function
    # indicators = {'roe': {
    #                       'attribute': 'data-reactid',
    #                       'value': re.compile(".*RETURN_ON_EQUITY\.1$"),
    #                       'transform': depercentize,
    #                       },
    #               'fcf': {
    #                       'attribute': 'data-reactid',
    #                       'value': re.compile(".*LEVERED_FREE_CASH_FLOW\.1$"),
    #                       'transform': cash_to_float,
    #                       },
    #               'ev2ebitda': {
    #                       'attribute': 'data-reactid',
    #                       'value': re.compile(".*ENTERPRISE_VALUE_TO_EBITDA\.1$"),
    #                       },
    #               }
    indicators = {'roe': {
                          'tag': 'span',
                          'attribute': 'class',
                          'value': re.compile("^Return on Equity$"),
                          'transform': depercentize,
                          },
                  'fcf': {
                          'tag': 'span',
                          'attribute': 'class',
                          'value': re.compile("^Levered Free Cash Flow$"),
                          'transform': cash_to_float,
                          },
                  'ev2ebitda': {
                          'tag': 'span',
                          'attribute': 'class',
                          'value': re.compile("^Enterprise Value/EBITDA$"),
                          },
                  }

    if count:
        r = requests.get("{}{}/company/?count={}".format(host, api_url, count), auth=auth)
    else:
        print "get sector and industry "
        total = requests.get("{}{}/company/".format(host, api_url), auth=auth).json().get('total')
        r = requests.get("{}{}/company/?count={}".format(host, api_url, total), auth=auth)

    try:
        companies = sorted(r.json().get('companies'), key=lambda x: x['symbol'])
    except ValueError as e:
        print e.message
        print r
        sys.exit(1)

    # if r.status_code != 200:
    #     return

    symbols = [company['symbol'] for company in companies]

    # companies = Company.query.with_entities(Company.symbol).all()
    # symbols = [company[0] for company in companies]

    print("Iterate through symbols")

    for symbol in symbols:
        print("{} Fetching {}  :".format(time.strftime("%H:%M:%S"), symbol))

        #driver = MyWebDriver()
        retry_current = 0
        retry_limit = 5
        while retry_current < retry_limit:
            try:
                driver = PhantomJS()
            except URLError:
                time.sleep(retry_current**2)
            retry_current += 1

        driver.set_window_size(1120, 550)
        driver.get(yahoo_url.format(symbol, symbol))
        try:
            #WebDriverWait(driver, 10).until(EC.title_contains("AAPL Key Statistics | Apple Inc. Stock - Yahoo Finance"))
            #element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "td[reactid]")))
            #element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//td[@data-reactid[ends-with(., 'RETURN_ON_EQUITY.1')]]")))

            # these two seem to work...
            #element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@data-reactid,'RETURN_ON_EQUITY.1')]")))
            #element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[substring(@data-reactid, string-length(@data-reactid) - string-length('RETURN_ON_EQUITY.1') +1) = 'RETURN_ON_EQUITY.1']")))
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[text()='Return on Equity']")))
            # time.sleep(5)

            #"//input[@id[ends-with(.,'register')]]"
        except TimeoutException as e:
            print "Caught", e
            print driver.title
            print "continuing..."
            continue

        soup = BeautifulSoup(driver.page_source, "lxml")

        d = {'symbol': symbol}
        for indicator in indicators.keys():
            curr_ind = indicators[indicator]
            s = soup.find_all(curr_ind['tag'], text=curr_ind['value'])[0].find_next('td', attrs={'class': 'Fz(s) Fw(500) Ta(end)'}).text
            print indicator, s

            # for element in s:
            if curr_ind.has_key('transform'):
                f = curr_ind['transform']
                #print(f(element.text))
                d[indicator] = f(s)
            else:
                #print(element.text)
                d[indicator] = s

        print "Fetched indicator from source:", d
        r = requests.post("{}{}/indicators".format(host, api_url), auth=auth, json=d)

        if r.status_code == 201:
            print "success"
        elif r.status_code == 409:
                print "duplicate, won't add"
        else:
            print "Failed with", r.status_code


if __name__ == '__main__':
    get_ratio_data()
