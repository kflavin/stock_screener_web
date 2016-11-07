import requests


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

