from datetime import datetime, date
from flask import jsonify, request, abort, url_for
from sqlalchemy import distinct
from sqlalchemy.exc import IntegrityError

from .errors import bad_request, conflict
from . import api as api_1_0
from ..models import Indicators, Company
from .. import db


@api_1_0.route('/indicators/<int:id>')
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


@api_1_0.route('/indicators/<int:id>/dates')
def get_indicator_dates(id):
    company = Company.query.filter_by(id=id).first()
    dates = company.dates_to_json()
    if not dates:
        abort(404)

    return jsonify({'dates': dates})


@api_1_0.route('/indicators', methods=['POST'])
def create_indicators():
    indicator = Indicators.from_json(request.json)
    print "indicator given ", indicator.ev2ebitda, indicator.fcf

    if not indicator.is_duplicate_of_last():
        try:
            db.session.add(indicator)
            db.session.commit()
        except IntegrityError:
            return conflict("Could not create indicator, likely a duplicate date.")
        else:
            return jsonify(indicator.to_json()), 201, {'Location': url_for('api_1_0.get_indicators', id=indicator.id,_external=True) }
    else:
        db.session.delete(indicator)
        db.session.commit()

    return conflict("Identical indicator exists")
