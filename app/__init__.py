import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask.ext.security import Security, SQLAlchemyUserDatastore
from utils import convert_to_cash

# Setup Flask-Security
security = Security()
db = SQLAlchemy()

# Stock Database specific
#from sqlalchemy import create_engine, desc, asc
#from sqlalchemy.ext.automap import automap_base
#from sqlalchemy.orm import Session

# Setup a session to read the stocks app database
#Base = automap_base()
# using environment variables for now..
#engine = create_engine("%s://%s:%s@%s/%s" % (os.environ['swtype'],
#                                             os.environ['swuser'],
#                                             os.environ['swpassword'],
#                                             os.environ['swhost'],
#                                             os.environ['swdatabase'])
#                       )
#Base.prepare(engine, reflect=True)
#Company = Base.classes.company
#Indicators = Base.classes.indicators
#session = Session(engine)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    db.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Add custom functions to Jinja templates
    from app.main.pages import url_for_other_page
    app.jinja_env.globals.update(convert_to_cash=convert_to_cash)
    app.jinja_env.globals.update(url_for_other_page=url_for_other_page)
    app.jinja_env.globals['url_for_other_page'] = url_for_other_page

    return app

from app.models import User, Role
from app.main import views
