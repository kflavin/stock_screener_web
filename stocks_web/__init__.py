import os
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore
from utils import convert_to_cash
from stocks_web.pages import url_for_other_page
from flask import Flask

# Stock Database specific
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = '***REMOVED***://***REMOVED***:***REMOVED***@***REMOVED***/***REMOVED***'

# Add custom functions to Jinja templates
app.jinja_env.globals.update(convert_to_cash=convert_to_cash)
app.jinja_env.globals.update(url_for_other_page=url_for_other_page)
#app.jinja_env.globals['url_for_other_page'] = url_for_other_page

# Setup a session to read the stocks app database
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

# Create database connection object for website specific models
db = SQLAlchemy(app)

from stocks_web import views
from stocks_web.models import User, Role

