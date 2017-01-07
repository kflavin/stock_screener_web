from datetime import date
from json import JSONEncoder
from math import ceil
from flask import request, url_for
from sqlalchemy import func

from werkzeug.routing import BaseConverter

from app.models import Indicators, Company
from lib.siccodes import codes

def float_or_none(value):
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        return None


def depercentize(percentage):
    """
    turn a percentage into a float
    """
    try:
        clean_perc = percentage.replace(",", "")
    except AttributeError as e:
        return None

    if percentage:
        try:
            return round(float(clean_perc), 2)
        except ValueError as e:
            if clean_perc.endswith("%"):
                return round(float(clean_perc[0:-1]), 2)

    return None

def round_float(value, precision=2):
    """
    If value is a float, round it.  For presentation.
    """
    if value:
        try:
            return "{:.{}f}".format(round(float(value), precision), precision)
        except (ValueError, AttributeError) as e:
            return None


def cash_to_float(amount):
    """
    Takes a "user-friendly" cash value, like 100M, and tries to convert it to a float.
    """

    suffixes = {
                'k': 3,
                'm': 6,
                'b': 9,
                't': 12,
                'p': 15,
                }

    if amount:
        try:
            quotient = float(amount)
            #return "{:.2f}".format(quotient)     # already a float!
            return round(quotient, 2)
        except ValueError as e:
            suffix = amount[-1].lower()

            if suffixes.has_key(suffix):
                #return "{:.2f}".format(float(amount[0:-1]) * (10**suffixes[suffix]))
                return round(float(amount[0:-1]) * (10**suffixes[suffix]), 2)

    return None



def convert_to_cash(amount):
    """
    Convert dollar amounts into shorter values.
    """

    try:
        quotient = int(float(amount))
    except TypeError as e:
        return "None"

    # Account for Python rounding down negative numbers with integer division,
    # -1 / 1000 = -1 :(
    negative = False
    if quotient < 0:
        quotient = quotient * -1
        negative = True

    starting_amount = quotient
    counter = 0
    while True:
        modulus = quotient % 1000
        quotient = quotient / 1000
        if quotient == 0:
            break
        counter += 1

    if counter == 1:
        suffix = "K"
    elif counter == 2:
        suffix = "M"
    elif counter == 3:
        suffix = "B"
    elif counter == 4:
        suffix = "T"
    elif counter == 5:
        suffix = "P"
    else:
        suffix = ""

    divisor = 1.0
    for i in xrange(1, counter+1):
        divisor *= 1000.0

    total = round(starting_amount / divisor, 2)
    # Flip back to negative if it was negative...
    if negative:
        total *= -1

    return "%.2f%s" % (total, suffix,)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


class DateToJSON(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)


def get_industry(sic_code):
    return codes.get(str(sic_code))


def get_averages(type, search):
    """
    Return a dictionary with averages for each indicator in the given sector
    Args:
        type: sector or industry
        sector: search string

    Returns: dict of averages with indicator as key

    """
    # entities to display for averages
    entities = get_entities(with_symbol=False)
    wrapped_entities = []
    for entity in entities:
        wrapped_entities.append(func.avg(entity).label(entity.key))

    averages_d = {}
    if search is not None:
        stmt1 = db.session.query(Indicators.company_id, func.max(Indicators.id).label('max_id')).group_by(
            Indicators.company_id
        ).subquery()
        stmt2 = db.session.query(Company, stmt1.c.max_id).join(stmt1, stmt1.c.company_id == Company.id).filter(
            setattr(Company, type, search)
        ).subquery()
        averages = db.session.query(*wrapped_entities). \
            join(stmt2, stmt2.c.max_id == Indicators.id). \
            filter((Indicators.roe != None) & (Indicators.fcf != None) & (Indicators.ev2ebitda != None)). \
            first()

        for e in entities:
            averages_d[e.key] = getattr(averages, e.key)

    return averages_d


def get_entities(with_symbol=True, with_date=False):
    order_bys = Indicators.get_attributes(with_symbol=with_symbol)

    # configure models (for determining column model) and entities (for retrieving columns)
    entities = []
    models = []
    for o in order_bys:
        if o.find(".") != -1:
            entities.append(eval(o))
            models.append(o.split(".")[0])
        else:
            entities.append(eval("Indicators." + o))
    if with_date:
        entities.append(Indicators.date)

    return entities
