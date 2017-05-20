from flask import Flask
from flask_bcrypt import Bcrypt
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.urls import url_quote_plus

from config import config
from flask.ext.security import Security, SQLAlchemyUserDatastore
from utils import convert_to_cash, get_industry
from flask_mail import Mail
from .utils import RegexConverter

# Setup Flask-Security
security = Security()
bcrypt = Bcrypt()
db = SQLAlchemy()
mail = Mail()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.url_map.converters['regex'] = RegexConverter

    config[config_name].init_app(app)
    db.init_app(app)
    mail.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)
    bcrypt.init_app(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Add custom functions to Jinja templates
    from app.main.pages import url_for_other_page
    app.jinja_env.globals.update(convert_to_cash=convert_to_cash)
    app.jinja_env.globals.update(get_industry=get_industry)
    app.jinja_env.globals.update(url_for_other_page=url_for_other_page)
    app.jinja_env.globals.update(url_quote_plus=url_quote_plus)
    app.jinja_env.globals['url_for_other_page'] = url_for_other_page

    # Custom filters
    from app.utils import round_float
    app.jinja_env.filters['round_float'] = round_float

    # Custom test
    #from app.utils import is_float
    #app.jinja_env.tests['float'] = is_float

    from .api_1_0 import api as api_1_0_0_blueprint
    app.register_blueprint(api_1_0_0_blueprint, url_prefix='/api/1.0')

    from .api_2_0 import api as api_2_0_0_blueprint
    app.register_blueprint(api_2_0_0_blueprint, url_prefix='/api/2.0')

    return app

from app.models import User, Role
from app.main import views
