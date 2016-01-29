import os
from math import ceil
#import re

# Flask specific
from flask import Flask, render_template, redirect, \
       send_from_directory
from flask_login import logout_user
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required


# Stock Database specific
from sqlalchemy import create_engine, desc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# App imports
from utils import convert_to_cash, Pagination, url_for_other_page

Base = automap_base()
# using environment variables for now..
engine = create_engine("%s://%s:%s@%s/%s" % (os.environ['swtype'],
                                             os.environ['swuser'],
                                             os.environ['swpassword'],
                                             os.environ['swhost'],
                                             os.environ['swdatabase'])
                       )
Base.prepare(engine, reflect=True)
Company = Base.classes.company
Indicators = Base.classes.indicators
session = Session(engine)

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

# Add custom function to Jinja template
app.jinja_env.globals.update(convert_to_cash=convert_to_cash)
app.jinja_env.globals.update(url_for_other_page=url_for_other_page)
#app.jinja_env.globals['url_for_other_page'] = url_for_other_page

# Create database connection object
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_user(email='admin', password='password')
    db.session.commit()

# Views
@app.route('/')
@login_required
def home():
    """
    Welcome screen
    """
    c = session.query(Company).filter_by(symbol="AAPL").all()[0]
    context = {'symbol': c.symbol}
    return render_template('index.html', company=context)

PER_PAGE = 100
def get_listings(page, buy=True, date=None, roe=15.0):
    """
    """

    if not date:
        date = session.query(Indicators).order_by(desc('date')).limit(1).all()[0].date

    count = session.query(Indicators).filter(Indicators.buy == True).filter(Indicators.date == \
            date.strftime("%Y-%m-%d")).filter(Indicators.roe > roe).count()
    print "count is", count

    # Flask handles, unnecessary?
    ## Sanitize input, then calculate first record.
    #if re.match(r"\d+", str(offset)):
    #    start = offset * (PER_PAGE-1)
    #else:
    #    start = 0
    pages = ceil(count / float(PER_PAGE))

    if page > pages:
        page = pages
    elif page < 0:
        page = pages

    start = (page-1) * PER_PAGE
    last = start + PER_PAGE

    print "retrieving", start, last
    listings = session.query(Indicators).filter(Indicators.buy == True).filter(Indicators.date == \
            date.strftime("%Y-%m-%d")).filter(Indicators.roe > roe).slice(start, last).all()
    return listings, count

#@app.route('/listings')
@app.route('/listings/', defaults={'page': 1})
@app.route('/listings/page/<int:page>')
@login_required
def listings(page):
    """
    Show most recent listings.
    """
    # Get most recent date


    listings, count = get_listings(page)
    print "page", page, "count", count

    #pagination = Pagination(page, PER_PAGE, count)
    pagination = Pagination(1, 20, 100)
    return render_template('listings.html', 
                           pagination=pagination,
                           listings=listings,
                           count=count)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/css/<path:path>')
def send_css(path):
    print "Your path is", path
    return send_from_directory('static/css', path)

if __name__ == '__main__':
    app.run()
