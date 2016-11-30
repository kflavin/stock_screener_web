from sqlalchemy.exc import IntegrityError
from flask import request, current_app, url_for, jsonify, abort
from errors import conflict, bad_request
from ..models import Company
from .. import db
from . import api


@api.route('/company/')
def get_companies():
    page = request.args.get('page', 1, type=int)
    pagination = Company.query.order_by(Company.name.asc()).paginate(page,
                                                                     per_page=current_app.config['COMPANIES_PER_PAGE'],
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
        'count': pagination.total
    })


@api.route('/company/<regex("[A-Za-z]{2,4}"):symbol>')
def get_company(symbol):
    company = Company.query.filter_by(symbol=symbol).first()
    if not company:
        abort(404)

    return jsonify(company.to_json())


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
    for company in request.json.get('companies'):
        print "Adding", company
        try:
            company = Company.from_json(company)
        except ValueError, e:
            # return bad_request("Invalid data.  Check symbol and company name.")
            print e
        else:
            db.session.add(company)
            try:
                db.session.commit()
                count += 1
            except IntegrityError:
                db.session.rollback()

    return jsonify({'count': count}), 201
