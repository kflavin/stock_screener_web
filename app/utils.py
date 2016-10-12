from datetime import date
from json import JSONEncoder
from math import ceil
from flask import request, url_for

from werkzeug.routing import BaseConverter


def depercentize(percentage):
    """
    turn a percentage into a float
    """
    if percentage:
        try:
            return round(float(percentage), 2)
        except ValueError as e:
            if percentage.endswith("%"):
                return round(float(percentage[0:-1]), 2)

    return 0.0



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

    return 0.0

    

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

