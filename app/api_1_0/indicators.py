from datetime import datetime, date
from flask import jsonify, request
from . import api
from ..models import Indicators


@api.route('/indicators/<int:id>')
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
    return jsonify(indicators.to_json())


@api.route('/indicators/<int:id>', methods=['POST'])
def set_indicators(id):
    pass
