from flask import request, current_app, url_for, jsonify, abort
from ..models import Company
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


@api.route('/company/<regex("[A-Z]{2,4}"):symbol>')
def get_company(symbol):
    company = Company.query.filter_by(symbol=symbol).first()
    if not company:
        abort(404)

    return jsonify(company.to_json())


#@api.route('/company/<int:id>', methods=['POST'])
@api.route('/company/<regex("[A-Z]{2,4}"):symbol>', methods=['POST'])
def new_company(symbol):
    #request.args.
    return jsonify({})
