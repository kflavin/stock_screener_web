from selenium.webdriver import PhantomJS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib2 import URLError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError
from app import db

class MyWebDriver(PhantomJS):
    def __init__(self, *a, **kw):
        super(MyWebDriver, self).__init__(*a, **kw)
        self._maxRequestCount = 100 
        self._RequestCount = 0 

    def get(self, url):
        if self._RequestCount > self._maxRequestCount:
            self.__reset()
        super(MyWebDriver, self).get(url)
        self._RequestCount += 1

    def __reset(self):
        try:
            self.quit()
        except:
            print("couldn't quit, do so manually")
        self.__dict__ = self.__class__().__dict__


def get_ratio_data():
    import re
    import time
    from bs4 import BeautifulSoup

    from app.models import Company, Indicators
    from app.utils import cash_to_float, depercentize


    # Dict item with list: element attribute, attribute value to look for, optional transform function
    indicators = {'roe': {
                          'attribute': 'data-reactid',
                          'value': re.compile(".*RETURN_ON_EQUITY\.1$"),
                          'transform': depercentize,
                          },
                  'fcf': {
                          'attribute': 'data-reactid',
                          'value': re.compile(".*LEVERED_FREE_CASH_FLOW\.1$"),
                          'transform': cash_to_float,
                          },
                  'ev2ebitda': {
                          'attribute': 'data-reactid',
                          'value': re.compile(".*ENTERPRISE_VALUE_TO_EBITDA\.1$"),
                          },
                  }


    companies = Company.query.with_entities(Company.symbol).all()
    symbols = [company[0] for company in companies]

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
        driver.get("http://finance.yahoo.com/quote/{}/key-statistics?p={}".format(symbol, symbol))
        try:
            #WebDriverWait(driver, 10).until(EC.title_contains("AAPL Key Statistics | Apple Inc. Stock - Yahoo Finance"))
            #element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "td[reactid]")))
            #element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//td[@data-reactid[ends-with(., 'RETURN_ON_EQUITY.1')]]")))

            # these two seem to work...
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[substring(@data-reactid, string-length(@data-reactid) - string-length('RETURN_ON_EQUITY.1') +1) = 'RETURN_ON_EQUITY.1']")))
            #element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@data-reactid,'RETURN_ON_EQUITY.1')]")))

            #"//input[@id[ends-with(.,'register')]]"
        except TimeoutException as e:
            print  "Caught", e
            print driver.title
            continue

        #time.sleep(5)

        #with open("{}.out".format(symbol), "w") as f:
        #    f.write(driver.page_source.encode('utf-8'))

        soup = BeautifulSoup(driver.page_source, "lxml")

        d = {'symbol': symbol}
        for indicator in indicators.keys():
            curr_ind = indicators[indicator]
            s = soup.find_all(attrs={curr_ind['attribute']: curr_ind['value']})
            print indicator, s

            for element in s:
                if curr_ind.has_key('transform'):
                    f = curr_ind['transform']
                    #print(f(element.text))
                    d[indicator] = f(element.text)
                else:
                    #print(element.text)
                    d[indicator] = element.text

        try:
            i = Indicators.from_json(d)
            if not i.is_duplicate_of_last():
                db.session.add(i)
                db.session.commit()
            else:
                db.session.delete(i)
                db.session.delete(i)
                db.session.commit()
                print "No change in indicator, so don't save it", i
        except (IntegrityError, UnmappedInstanceError) as e:
            print "Caught", e
            db.session.rollback()

        print "indicators", d
        #time.sleep(3)

if __name__ == '__main__':
    get_ratio_data()
