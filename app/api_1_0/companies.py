from sqlalchemy.exc import IntegrityError
from flask import request, current_app, url_for, jsonify, abort
from errors import conflict, bad_request
from ..models import Company
from .. import db
from . import api


@api.route('/company/', methods=['GET'])
def get_companies():

    try:
        count = int(request.args.get('count'))
    except (ValueError, TypeError):
        count = current_app.config['COMPANIES_PER_PAGE']

    page = request.args.get('page', 1, type=int)
    pagination = Company.query.order_by(Company.name.asc()).paginate(page,
                                                                     per_page=count,
                                                                     error_out=False)
    companies = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_companies', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_companies', page=page+1, _external=True)

    return jsonify({
        'companies': [company.to_json() for company in companies],
        'prev': prev,
        'next': next,
        'total': pagination.total,
        'pages': pagination.pages,
        'per_page': pagination.per_page
    })


@api.route('/company/<regex("[A-Za-z]{2,4}"):symbol>', methods=['GET', 'POST'])
def get_company(symbol):
    company = Company.query.filter_by(symbol=symbol).first()
    if not company:
        abort(404)

    if request.method == "GET":
        return jsonify(company.to_json())
    elif request.method == "POST":
        d = request.json
        if d:
            d['symbol'] = symbol

            c = Company.update(d)
            if c:
                return jsonify(c.to_json()),201, {'Location': url_for('api.get_company',
                                                                      symbol=company.symbol,
                                                                      _external=True)
                                                  }
            else:
                return bad_request("Could not update {}".format(symbol))
        else:
            return bad_request("No data sent for {}".format(symbol))

    else:
        return bad_request("Invalid request.")


#@api.route('/company/<int:id>', methods=['POST'])
#@api.route('/company/<regex("[A-Z]{2,4}"):symbol>/', methods=['POST'])
@api.route('/company/', methods=['POST'])
def add_company():
    try:
        company = Company.from_json(request.json)
    except ValueError:
        return bad_request("Invalid data.  Check symbol and company name.")

    db.session.add(company)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return conflict("Value already exists.")
    else:
        return jsonify(company.to_json()), 201, {'Location': url_for('api.get_company',
                                                                     symbol=company.symbol,
                                                                     _external=True)
                                                 }


@api.route('/company/bulk/', methods=['POST'])
def bulk_add_company():
    # print request.json.get('companies')

    count = 0
    for c in request.json.get('companies'):
        try:
            company = Company.from_json(c)
        except ValueError, e:
            # return bad_request("Invalid data.  Check symbol and company name.")
            print "Could not add", c, e
        else:
            db.session.add(company)
            try:
                db.session.commit()
                count += 1
            except IntegrityError:
                db.session.rollback()

    return jsonify({'count': count}), 201

