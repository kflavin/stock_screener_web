from math import ceil
from flask import request, url_for

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


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)

