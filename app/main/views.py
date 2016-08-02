from math import ceil
from flask import Flask, render_template, redirect, \
       send_from_directory, request
from flask.ext.security import login_required
from flask_login import logout_user
#from app import app, db
#from app import session, Indicators, Company, desc, asc
#from app import desc, asc
from sqlalchemy import create_engine, desc, asc
from app.main.pages import Pagination
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
    c = db.session.query(Company).filter_by(symbol="AAPL").all()[0]
    context = {'symbol': c.symbol}
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

#@app.route('/listings')
@main.route('/listings/', defaults={'page': 1})
@main.route('/listings/<int:page>')
@login_required
def listings(page):
    """
    Show most recent listings.
    """
    # Get most recent date

    sort = request.args.get('sort') if request.args.get('sort') else "roe"
    reverse = True if request.args.get('reverse') == "True" else False
    flip = False if reverse else True

    listings, count = get_listings(page, sort, reverse)

    pagination = Pagination(page, PER_PAGE, count)
    #pagination = Pagination(1, 20, 100)
    return render_template('listings.html', 
                           pagination=pagination,
                           listings=listings,
                           count=count,
                           sort=sort,
                           reverse=reverse,
                           flip=flip)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@main.route('/static/<path:path>')
def send_css(path):
    print "Your path is", path
    return send_from_directory('static/css', path)
