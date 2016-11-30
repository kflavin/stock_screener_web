import os
from populators.external.companies import get_symbol_lists
from requests.auth import HTTPBasicAuth


def get_company_details(throttle=True, count=0, index="NYSE"):
    """
    throttle: true = 1 second wait between requests
    Count < 1 implies get all
    index: NYSE or NASDAQ

    """
    import time
    import requests
    import string
    from bs4 import BeautifulSoup

    curr = 0

    user = os.environ.get('CLI_USER')
    password = os.environ.get('CLI_PASSWORD')
    host = os.environ.get('CLI_HOST')
    auth = HTTPBasicAuth(user, password)


    break_out = False
    for c in string.uppercase:
        r = get_symbol_lists(index, c)
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
                data = {'name': name, 'symbol': symbol, 'index': index}
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

        r = requests.post("http://{}/api/1.0/company/bulk/".format(host), json={'companies': batch}, auth=auth)
        print r
        print "code", r.status_code

        if throttle:
            time.sleep(1)

        if break_out:
            break


if __name__ == '__main__':
    get_company_details()
