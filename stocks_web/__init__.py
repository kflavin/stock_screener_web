import os
from flask.ext.security import Security, SQLAlchemyUserDatastore
from utils import convert_to_cash
from stocks_web.pages import url_for_other_page
from stocks_web.models import db
from flask import Flask
from flask_mail import Mail

# Stock Database specific
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# Create app
app = Flask(__name__)
app.config.from_object('stocks_web.config')
mail = Mail(app)

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

# Initialize website specific models
db.init_app(app)

from stocks_web.models import User, Role
from stocks_web import views
