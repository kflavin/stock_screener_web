from math import ceil
from flask import Flask, render_template, redirect, \
       send_from_directory, request, current_app, url_for
from flask.ext.security import login_required
from flask_login import logout_user
#from app import app, db
#from app import session, Indicators, Company, desc, asc
#from app import desc, asc
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.sql.expression import nullslast
from app.main.pages import Pagination
from app.main.forms import FilterForm
from . import main
from .. import db
from ..models import Indicators, Company

from datetime import datetime

# Create a user to test with
#@main.before_first_request
#def create_user():
#    print "Creating everything......."
#    db.create_all()
#    if db.session.query(User).filter_by(email='admin').count() == 0:
#        user_datastore.create_user(email='admin', password='password', confirmed_at=datetime.now())
#    db.session.commit()


# Views
@main.route('/')
@login_required
def home():
    """
    Welcome screen
    """
    c = db.session.query(Company).first()
    #date = db.session.query(Indicators.date).order_by(desc("date")).distinct().limit(2).all()[-1].date
    if c:
        context = {'symbol': c.symbol}
    else:
        context = {'symbol': "No listings"}

    return render_template('index.html', company=context)


PER_PAGE = 50


def get_listings(page, sort_field, reverse=False, buy=True, date=None, roe=0.15, pm=10.0, om=10.0, tde=100.0):
    """
    """
    # Set the sort field
    if hasattr(Indicators, str(sort_field)):
        sorter = sort_field
    elif sort_field == "symbol":
        sorter = "Company.symbol"
    else:
        sorter = "roe"

    if reverse:
        sorter = asc(sort_field)
    else:
        sorter = desc(sort_field)

    if not date:
        # Look for the second to last date we had values...
        #date = session.query(Indicators).order_by(desc('date')).limit(1).all()[0].date
        date = db.session.query(Indicators.date).order_by(desc(Indicators.date)).distinct().limit(2).all()[-1].date

    # We need the count ahead of time to figure out the pagination.
    count = db.session.query(Indicators).\
            filter(Indicators.date == date.strftime("%Y-%m-%d")).\
            filter(Indicators.roe > roe).\
            count()
    #count = db.session.query(Indicators).\
    #        filter(Indicators.buy == True).\
    #        filter(Indicators.date == date.strftime("%Y-%m-%d")).\
    #        filter(Indicators.roe > roe).\
    #        filter(Indicators.pm > pm).\
    #        filter(Indicators.tde < tde).\
    #        count()

    if count == 0:
        pages = 1
    else:
        pages = ceil(count / float(PER_PAGE))

    if page > pages:
        page = pages
    elif page < 0:
        page = pages

    start = (page-1) * PER_PAGE
    last = start + PER_PAGE

    # sorting on a symbol requires a join
    if sort_field == "symbol":
        #listings = db.session.query(Indicators).\
        #        join(Company, Company.id == Indicators.company_id).\
        #        filter(Indicators.buy == True).\
        #        filter(Indicators.date == date.strftime("%Y-%m-%d")).\
        #        filter(Indicators.roe > roe).\
        #        filter(Indicators.pm > pm).\
        #        filter(Indicators.tde < tde).\
        #        order_by(sorter).\
        #        slice(start, last).\
        #        all()
        listings = db.session.query(Indicators).\
                join(Company, Company.id == Indicators.company_id).\
                filter(Indicators.date == date.strftime("%Y-%m-%d")).\
                filter(Indicators.roe > roe).\
                order_by(sorter).\
                slice(start, last).\
                all()
    else:
        #listings = db.session.query(Indicators).\
        #        filter(Indicators.buy == True).\
        #        filter(Indicators.date == \
        #        date.strftime("%Y-%m-%d")).\
        #        filter(Indicators.roe > roe).\
        #        filter(Indicators.pm > pm).\
        #        filter(Indicators.tde < tde).\
        #        order_by(sorter).\
        #        slice(start, last).\
        #        all()
        listings = db.session.query(Indicators).\
                filter(Indicators.date == \
                date.strftime("%Y-%m-%d")).\
                filter(Indicators.roe > roe).\
                order_by(sorter).\
                slice(start, last).\
                all()

    return listings, count


@main.route('/company/', defaults={'page': 1})
@main.route('/company/<int:page>')
@login_required
def company(page):
    """
    List of all companies we're tracking.
    """
    order_bys = Company.get_attributes()
    order_bys_no_fk = Company.get_attributes_no_fk()

    if request.args.get("direction") == "False":
        direction = False
    else:
        direction = True

    if request.args.get('order_by') in order_bys:
        order_by = request.args.get('order_by')
    else:
        order_by = "symbol"

    which_way = "asc" if direction == True else "desc"
    order = getattr(getattr(Company, order_by), which_way)()

    #pagination = Company.query.order_by(Company.symbol.desc()).paginate(page, current_app.config['COMPANIES_PER_PAGE'], error_out=False)
    pagination = Company.query.order_by(order).paginate(page, current_app.config['COMPANIES_PER_PAGE'], error_out=False)
    companies = pagination.items

    total = Company.query.count()

    return render_template('company.html',
                           pagination=pagination,
                           companies = companies,
                           order_by = order_by,
                           direction = direction,
                           order_bys = order_bys_no_fk,
                           total=total
                           )

@main.route('/company/<string:symbol>/')
def company_detail(symbol):
    """
    Return company details
    """
    attributes = Indicators.get_attributes_no_fk()
    company = Company.query.filter(Company.symbol == symbol).first()
    indicators = Indicators.query.filter(Indicators.company_id == company.id).all()
    return render_template('company_detail.html', company = company, indicators=indicators, attributes=attributes)



@main.route('/indicator/<string:symbol>/', defaults={'page': 1})
@main.route('/indicator/<string:symbol>/<int:page>')
@login_required
def get_indicator(symbol, page):
    sort = request.args.get('sort') if request.args.get('sort') else "roe"
    reverse = True if request.args.get('reverse') == "True" else False
    flip = False if reverse else True

    c = Company.query.filter_by(symbol=symbol).first()
    indicators = c.indicators.all()
    count = len(indicators)


    pagination = Pagination(page, PER_PAGE, count)

    return render_template('indicator.html',
                           pagination=pagination,
                           indicators = indicators,
                           count=count,
                           sort=sort,
                           reverse=reverse,
                           flip=flip
                           )

@main.route('/listings/', defaults={'page': 1}, methods=['GET', 'POST'])
@main.route('/listings/<int:page>', methods=['GET', 'POST'])
@login_required
def listings(page):
    """
    List of all companies we're tracking.

    order_bys: fields to order by.  assumes Indicator model, unless prefixed with the model name
    order_by: attribute value passed from client (no model)
    order_bys_no_fk: order_bys with no model prefixed.  this is passed to the template.
    """
    order_bys = Indicators.get_attributes()
    order_bys_no_fk = Indicators.get_attributes_no_fk()

    # configure models (for determing column model) and entities (for retrieving columns)
    entities = []
    models = []
    for o in order_bys:
        if o.find(".") != -1:
            entities.append(eval(o))
            models.append(o.split(".")[0])
        else:
            entities.append(eval("Indicators."+o))

    # Search filter, redirect if it exists
    form = FilterForm()
    #filter_by = form.filter.data if form.validate_on_submit() else None

    if form.is_submitted():
        if form.validate():
            direction = request.args.get('direction')
            order_by = request.args.get('order_by')
            query_state = {}
            if direction:
                query_state['direction'] = direction
            if order_by:
                query_state['order_by'] = order_by

            return redirect(url_for('main.listings', page=page, filter_by=form.filter.data, **query_state))
        else:
            filter_by = ""
    else:
        if Company.validate_symbol(request.args.get('filter_by', '').upper()):
            filter_by = request.args.get('filter_by')
        else:
            filter_by = ''

    print "your filter by is", filter_by

    #if form.validate_on_submit():
    #    direction = request.args.get('direction')
    #    order_by = request.args.get('order_by')
    #    query_state = {}
    #    if direction:
    #        query_state['direction'] = direction
    #    if order_by:
    #        query_state['order_by'] = order_by

    #    return redirect(url_for('main.listings', page=page, filter_by=form.filter.data, **query_state))

    #if Company.validate_symbol(request.args.get('filter_by', '').upper()):
    #    filter_by = request.args.get('filter_by')
    #else:
    #    filter_by = ''

    # Get values from client
    if request.args.get("direction") == "False":
        direction = False
    else:
        direction = True

    if request.args.get('order_by') in order_bys_no_fk:
        order_by = request.args.get('order_by')
    else:
        #order_by = "company.symbol"
        order_by = "roe"

    which_way = "asc" if direction == True else "desc"

    # Set the order based on the order_by that has been passed in.
    for model in models:
        if model+"."+order_by in order_bys:
            order = getattr(getattr(eval(model), order_by), which_way)()
        else:
            order = getattr(getattr(Indicators, order_by), which_way)()


    # get the most recent collection date
    try:
        #date = db.session.query(Indicators.date).order_by(desc("date")).distinct().limit(2).all()[-1].date # second to last day
        date = db.session.query(Indicators.date).order_by(desc("date")).distinct().limit(2).all()[0].date   # last day
    except IndexError:
        return render_template('listings.html',
                               pagination=None,
                               listings = None,
                               order_by = order_by,
                               direction = direction,
                               order_bys = order_bys_no_fk,
                               date = datetime.today(),
                               count = 0,
                               form = form,
                               filter_by=filter_by
                               )
        
    #date = db.session.query(Indicators.date).order_by(order).distinct().limit(2).all()[-1].date
    #date = db.session.query(Indicators.date).order_by(desc(Indicators.date)).distinct().limit(2).all()[-1].date
    #db.session.query(Indicators).join(Company).filter(Indicators.date == date).order_by(Company.symbol).all()

    #pagination = Indicators.query.order_by(order).paginate(page, current_app.config['INDICATORS_PER_PAGE'], error_out=False)
    #pagination = db.session.query(Indicators).join(Company).filter(Indicators.date == date).order_by(Company.symbol).paginate(page, current_app.config['INDICATORS_PER_PAGE'], error_out=False)

    # Build our query
    query = Indicators.query.join(Company)
    if filter_by:
        #query = query.filter((Indicators.date == date) & ( Company.symbol.startswith("{}".format(filter_by)) | Company.name.startswith("{}".format(filter_by)) )  )
        query = query.filter((Indicators.date == date) & ( Company.symbol.ilike("{}".format(filter_by)))  )
    else:
        query = query.filter(Indicators.date == date)

    query = query.distinct(*entities)
    query = query.order_by(nullslast(order))
    query = query.with_entities(*entities)

    pagination = query.paginate(page, current_app.config['INDICATORS_PER_PAGE'], error_out=False)
    listings = pagination.items

    return render_template('listings.html',
                           pagination=pagination,
                           listings = listings,
                           order_by = order_by,
                           direction = direction,
                           order_bys = order_bys_no_fk,
                           date = datetime.today(),
                           count = pagination.total,
                           form = form,
                           filter_by=filter_by
                           )


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@main.route('/static/<path:path>')
def send_css(path):
    print "Your path is", path
    return send_from_directory('static/css', path)
