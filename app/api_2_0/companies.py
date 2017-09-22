from sqlalchemy.exc import IntegrityError
from flask import request, current_app, url_for, jsonify, abort, g
from errors import conflict, bad_request
from ..models import Company
from .. import db
from .authentication import login_required
from . import api as api_2_0
# add following to views that need auth (after the api_2_0.route decorator)
# from .authentication import auth
# @auth.login_required


@login_required
@api_2_0.route('/company/', methods=['GET'])
def get_companies():
    """
    Query parameters:
        count: return "count" per page
        empty_only: if true return only companies with an empty industry or sector field.  else return all companies.
    Returns:
        json response

    """
    # Troubleshooting url map issues caused by decorators...
    # current_app.url_map

    try:
        count = int(request.args.get('count'))
    except (ValueError, TypeError):
        count = current_app.config['COMPANIES_PER_PAGE']

    if request.args.get('empty_only') == "True":
        empty_only = True
    else:
        empty_only = False

    page = request.args.get('page', 1, type=int)

    if empty_only:
        pagination = Company.query.filter((Company.sector == None) | (Company.industry == None)).\
            order_by(Company.name.asc()).paginate(page, per_page=count, error_out=False)
    else:
        pagination = Company.query.order_by(Company.name.asc()).\
            paginate(page, per_page=count, error_out=False)

    companies = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api_2_0.get_companies', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api_2_0.get_companies', page=page+1, _external=True)

    return jsonify({
        'companies': [company.to_json() for company in companies],
        'prev': prev,
        'next': next,
        'total': pagination.total,
        'pages': pagination.pages,
        'per_page': pagination.per_page
    })


@api_2_0.route('/company/<regex("[A-Za-z]{1,4}"):symbol>', methods=['GET', 'POST'])
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
                return jsonify(c.to_json()), 201, {'Location': url_for('api_2_0.get_company',
                                                                       symbol=company.symbol,
                                                                       _external=True)
                                                  }
            else:
                current_app.logger.debug("Failed to update company")
                return bad_request("Could not update {}".format(symbol))
        else:
            current_app.logger.debug("JSON request empty")
            return bad_request("No data sent for {}".format(symbol))

    else:
        return bad_request("Invalid request.")


#@api_2_0.route('/company/<int:id>', methods=['POST'])
#@api_2_0.route('/company/<regex("[A-Z]{2,4}"):symbol>/', methods=['POST'])
@api_2_0.route('/company/', methods=['POST'])
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
        return jsonify(company.to_json()), 201, {'Location': url_for('api_2_0.get_company',
                                                                     symbol=company.symbol,
                                                                     _external=True)
                                                 }


@api_2_0.route('/company/bulk/', methods=['POST'])
def bulk_add_company():
    print "Bulk adding companies"
    print request.json.get('companies')

    count = 0
    for c in request.json.get('companies'):
        print "c=", c
        try:
            print "ADding company", c
            company = Company.from_json(c)
        except ValueError, e:
            # return bad_request("Invalid data.  Check symbol and company name.")
            print "Could not add", c, e
        else:
            print "adding company under else"
            db.session.add(company)
            try:
                db.session.commit()
                count += 1
            except IntegrityError:
                db.session.rollback()

    return jsonify({'count': count}), 201

