from selenium.webdriver import PhantomJS
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
    import socket
    import re
    import time
    import dryscrape
    import webkit_server
    from random import randint
    from fake_useragent import UserAgent
    from bs4 import BeautifulSoup
    from selenium.webdriver import PhantomJS


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
                  }


    ua = UserAgent()


    #with open("10.csv", "r") as f:
    #with open("sp500-2.csv", "r") as f:
    with open("10_stocks", "r") as f:
        data = f.read()

    symbols = []
    for i in data.split("\n"):
        if i:

            symbols.append(i.split(",")[0])

    print("Iterate through symbols")
    ## dryscrape
    #session = dryscrape.Session()
    #session.set_header('User-Agent', ua.random)
    #session.set_timeout(5)

    for symbol in symbols:
        print("{} Fetching {}  :".format(time.strftime("%H:%M:%S"), symbol))

        import pdb; pdb.set_trace()
        #driver = MyWebDriver()
        driver = PhantomJS()
        driver.set_window_size(1120, 550)
        driver.get("http://finance.yahoo.com/quote/{}/key-statistics?p={}".format(symbol, symbol))

        ##try:
        ##    session = dryscrape.Session()
        ##except socket.error as e:
        ##    print("Failed to configure session {}".format(e))
        ##    continue

        ##session.set_header('User-Agent', ua.random)
        ##session.set_timeout(30)
        #try:
        #    #session.visit("http://finance.yahoo.com/quote/{}/key-statistics?p={}".format(symbol, symbol))
        #except Exception as e:
        #    print e, "try once more......"
        #    session.reset()
        #    time.sleep(5)
        #    session = dryscrape.Session()
        #    #session.set_header('User-Agent', ua.random)
        #    try:
        #        session.set_timeout(5)
        #        session.visit("http://finance.yahoo.com/quote/{}/key-statistics?p={}".format(symbol, symbol))
        #    except Exception as e:
        #        print e, "done trying..."
        #        session.reset()
        #        time.sleep(2)
        #        session = dryscrape.Session()
        #        continue


        #except socket.error as e:
        #    print("Failed to get {}, {} (1)".format(symbol, e))
        #    continue
        #except webkit_server.EndOfStreamError as e:
        #    print("Failed to get {}, {}, breaking (2)".format(symbol, e))
        #    continue
        #except webkit_server.InvalidResponseError as e:
        #    print("Failed to get {}, {}, breaking (3)".format(symbol, e))
        #    continue

        #response = session.body()
        #soup = BeautifulSoup(response, "lxml")

        with open("{}.out".format(symbol), "w") as f:
            f.write(driver.page_source.encode('utf-8'))

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
            db.session.add(Indicators.from_json(d))
            db.session.commit()
        except (IntegrityError, UnmappedInstanceError) as e:
            print "Caught", e
            db.session.rollback()

        print "indicators", d

        #wait = randint(1, 3)
        #print("Waiting {}".format(wait))
        #session.reset()
        #time.sleep(wait)


