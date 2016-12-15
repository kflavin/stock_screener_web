import os
from populators.external.companies import get_symbol_lists
from requests.auth import HTTPBasicAuth


def get_company_details(throttle=True, count=0, exchange="NYSE", host="http://127.0.0.1:5000", user="user", password="password"):
    """
    throttle: true = 1 second wait between requests
    Count < 1 implies get all
    exchange: NYSE or NASDAQ

    """
    import time
    import requests
    import string
    from bs4 import BeautifulSoup

    curr = 0

    auth = HTTPBasicAuth(user, password)

    break_out = False
    for c in string.uppercase:
        r = get_symbol_lists(exchange, c)
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find_all("table", class_="quotes")[0]
        trs = table.find_all("tr")
        trs.pop(0)  # remove header row
        batch = []
        for tr in trs:
            symbol = tr.td.a.text
            name = tr.td.next_sibling.text
            print curr, "Add", symbol, name
            if symbol and name:
                data = {'name': name, 'symbol': symbol, 'exchange': exchange}
                batch.append(data)
                # r = requests.post("http://{}/api/1.0/company/".format(host), json=data, auth=auth)
                # if r.status_code == 409:
                #     print "Duplicate value for", symbol
                # elif r.status_code != 201:
                #     print r.status_code
                #     # print r.text
                #     print "Error: ", r.json()

            curr += 1
            if count > 0:
                if curr >= count:
                    break_out = True
                    break
        print "get", c
        r = requests.post("{}/api/1.0/company/bulk/".format(host), json={'companies': batch}, auth=auth)
        print "code", r.status_code, "count:", r.json().get('count')

        if throttle:
            time.sleep(1)

        if break_out:
            break



if __name__ == '__main__':
    get_company_details()
