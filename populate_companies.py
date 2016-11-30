from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError
from app.external.companies import get_symbol_lists

def get_company_details(throttle=True, count=0, exchange="NYSE"):
    """
    throttle: true = 1 second wait between requests
    Count < 1 implies get all
    index: NYSE or NASDAQ

    """
    import re
    import time
    import requests
    import string
    from bs4 import BeautifulSoup

    from app.models import Company, Indicators, Exchange
    from app.utils import cash_to_float, depercentize
    from app import db

    # Add the index if it doesn't exist
    if not Exchange.query.filter(Exchange.name == exchange).first():
        db.session.add(Exchange(name=exchange))
        db.session.commit()

    curr = 0
    if count > 0:
        print "Attempting to pull", count, "companies"
    else:
        print "Pull all companies"

    break_out = False
    for c in string.uppercase:
        r = get_symbol_lists(exchange, c)
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find_all("table", class_="quotes")[0]
        trs = table.find_all("tr")
        trs.pop(0)  # remove header row
        for tr in trs:
            symbol = tr.td.a.text
            name = tr.td.next_sibling.text
            print curr, "Add", symbol, name
            if symbol and name:
                try:
                    db.session.add(Company.from_json({'name': name, 'symbol': symbol, 'index': exchange}))
                    db.session.commit()
                except (IntegrityError, UnmappedInstanceError) as e:
                    print "Caught", e
                    db.session.rollback()
                except ValueError as e:
                    print "Invalid company name or symbol"
                    print e
                    db.session.rollback()

            curr += 1
            if count > 0:
                if curr >= count:
                    break_out = True
                    break

        if throttle:
            time.sleep(1)

        if break_out:
            break


if __name__ == '__main__':
    get_company_details()
