from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError
from app import db

def get_ratio_data():
    import socket
    import re
    import time
    import dryscrape
    import webkit_server
    from random import randint
    from fake_useragent import UserAgent
    from bs4 import BeautifulSoup

    from app.models import Company, Indicators
    from app.utils import cash_to_float, depercentize

    session = dryscrape.Session()
    #element = "data-reactid"
    #value = re.compile(".*RETURN_ON_EQUITY\.1$")


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


    with open("10.csv", "r") as f:
        data = f.read()

    symbols = []
    for i in data.split("\n"):
        if i:

            symbols.append(i.split(",")[0])

    print("Iterate through symbols")
    for symbol in symbols:
        print("{} Fetching {}  :".format(time.strftime("%H:%M:%S"), symbol))
        session = dryscrape.Session()
        session.set_header('User-Agent', ua.random)
        try:
            session.visit("http://finance.yahoo.com/quote/{}/key-statistics?p={}".format(symbol, symbol))
        except socket.error as e:
            print("Failed to get {}, {}".format(symbol, e))
            continue
        except webkit_server.EndOfStreamError as e:
            print("Failed to get {}, {}, breaking".format(symbol, e))
            continue
        except webkit_server.InvalidResponseError as e:
            print("Failed to get {}, {}, breaking".format(symbol, e))
            continue

        response = session.body()
        soup = BeautifulSoup(response, "lxml")

        d = {'symbol': symbol}
        for indicator in indicators.keys():
            curr_ind = indicators[indicator]
            s = soup.find_all(attrs={curr_ind['attribute']: curr_ind['value']})

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
        except (IntegrityError, UnmappedInstanceError) as e:
            db.session.rollback()

        wait = randint(1, 10)
        print("Waiting {}".format(wait))
        time.sleep(wait)


