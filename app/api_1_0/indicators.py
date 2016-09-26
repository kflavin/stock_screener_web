from datetime import datetime, date
from flask import jsonify, request, abort
from sqlalchemy import distinct
from . import api
from ..models import Indicators, Company
from .. import db


@api.route('/indicators/<int:id>/')
def get_indicators(id):
    mydate = request.args.get('date', None)

    try:
        date_obj = datetime.strptime(mydate, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        date_obj = None

    if date_obj:
        indicators = Indicators.query.filter_by(company_id=id).filter_by(date=date_obj).first()
    else:
        indicators = Indicators.query.filter_by(company_id=id).order_by(Indicators.date.desc()).first()

    if not indicators:
        abort(404)

    return jsonify({'indicators': indicators.to_json()})


@api.route('/indicators/<int:id>/dates/')
def get_indicator_dates(id):
    company = Company.query.filter_by(id=id).first()
    dates = company.dates_to_json()
    if not dates:
        abort(404)

    return jsonify({'dates': dates})


@api.route('/indicators/<int:id>/', methods=['POST'])
def create_indicators(id):
    indicators = Indicators.from_json(request.json)
    db.session.add(indicators)
    db.session.commit()
