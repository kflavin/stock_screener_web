import json
import uuid
from calendar import timegm

import jwt
import datetime
from datetime import date
import re
import requests
import sys
from sqlalchemy import UniqueConstraint, desc, func, Float
#from flask.ext.security.utils import verify_password
#from flask.ext.security import UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy
from random import seed, choice
from string import ascii_uppercase
from flask import current_app, abort
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import bindparam
from sqlalchemy import inspect

# from app.external.companies import get_name_from_symbol

from app import db, bcrypt
from app.utils import DateToJSON, float_or_none


# Define models
from populators.external.companies import get_name_from_symbol

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)
    last_password_change = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    registration_code = db.Column(db.String(36))
    companies = db.relationship('Company', backref='user', lazy='dynamic')

    def __init__(self, email, password, active=False, confirmed_at=datetime.datetime.utcnow):
        self.email = email
        self.password = bcrypt.generate_password_hash(password, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        self.active = active
        self.registration_code = str(uuid.uuid4())
        if callable(confirmed_at):
            self.confirmed_at = confirmed_at()
        else:
            self.confirmed_at = confirmed_at

    def encode_auth_token(self, user_id, exp=86400):
        """
        Generate auth token
        :param user_id: 
        :param exp: token expiration in seconds, set in global config per environment
        :return: the encoded payload or exception on error
        """
        user = User.query.filter_by(id=user_id).first()
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=exp),
                'iat': datetime.datetime.utcnow(),
                'id': user_id,
                # Need this to serialize datetime like exp and iat.  In their case, it's handled in the jwt module
                'last_password_change': timegm(user.last_password_change.utctimetuple())
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            current_app.logger.debug(e)
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decode auth token
        :param auth_token: 
        :return: user id (int) or error string
        """
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            user_id = payload.get('id')

            if user_id:
                user = User.query.filter_by(id=user_id).first()
                last_reported_password_change = payload.get('last_password_change')
                last_actual_password_change = timegm(user.last_password_change.utctimetuple())
                if user and (last_reported_password_change >= last_actual_password_change):
                    return user_id

            return 'Signature expired.  Please log in again.'
        except jwt.ExpiredSignature:
            return 'Signature expired.  Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token.  Please log in again'

    def set_password(self, password):
        """
        Change the password, and update the timestamp so we can verify it against the token
        :param password: new password string 
        :return:
        """
        self.password = bcrypt.generate_password_hash(password, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        self.last_password_change = func.now()
        db.session.add(self)
        db.session.commit()

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def to_json(self):
        indicators = {}
        for k,v in self.get_attributes_no_fk().iteritems():
            if k == "symbol":
                indicators[k] = self.company.symbol
            else:
                indicators[k] = getattr(self, k)

        indicators['id'] = self.id
        indicators['date'] = self.date.isoformat()

        return indicators

    #@property
    #def password(self):
    #    raise AttributeError('password not a readable attribute')

    #@password.setter
    #def password(self, password):
    #    self.password = encrypt_password(password)

    # def verify_password(self, password):
    #     return verify_password(password, self.password)

    strategy = db.relationship('Strategy', backref='user', lazy='dynamic')

    def __repr__(self):
        return "<Userid: {0}, Email: {1}>".format(self.id, self.email)


class BlacklistToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    @staticmethod
    def check_blacklist(auth_token):
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

    def __repr__(self):
        return '<id: token: {}'.format(self.token)


class Strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    public = db.Column(db.Boolean, default=True)
    filter = db.relationship('Filters', backref='strategy', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Filters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roe = db.Column(db.Float, default=0.15)
    fcf = db.Column(db.Float, default=0)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'))


ExchangeMembership = db.Table('exchange_membership',
       db.Column('exchange_id', db.Integer, db.ForeignKey('exchange.id')),
       db.Column('company_id', db.Integer, db.ForeignKey('company.id'))
)


class Exchange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    companies = db.relationship('Company',
                                secondary=ExchangeMembership,
                                backref=db.backref('exchanges', lazy='dynamic'),
                                lazy='dynamic'
                                )

    @staticmethod
    def add_exchange(name):
        if name == "NYSE" or name == "NASDAQ":
            exchange = Exchange(name=name)
            return exchange
        else:
            return None

    @staticmethod
    def get_exchange(name):
        exchange = Exchange.query.filter(Exchange.name == name).first()
        if not exchange:
            exchange = Exchange.add_exchange(name)
        return exchange


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    symbol = db.Column(db.String(20), nullable=False, unique=True)
    sic_code = db.Column(db.Integer, nullable=True)
    sector = db.Column(db.String(200), nullable=True)
    industry = db.Column(db.String(200), nullable=True)
    active = db.Column(db.Boolean, default=True)
    indicators = db.relationship('Indicators', backref='company', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # "Special" attributes that we ignore
    ignore_attrs = ['id', 'indicators']

    # Define attributes here for lookups.
    attributes = {'name': "Name",
                  'symbol': "Ticker",
                  "sic_code": "SIC",
                  "sector": "Sector",
                  "industry": "Industry",
                  }

    @staticmethod
    def generate_symbol():
        seed()
        symbol = ""
        sym_len = int(choice("34")) + 1
        for i in range(1,sym_len):
            symbol += choice(ascii_uppercase)
        return symbol

    @classmethod
    def get_attributes(cls):
        return cls.attributes.keys()

    @classmethod
    def get_attributes_no_fk(cls):
        order_bys = cls.attributes.keys()
        order_bys_no_fk = {}
        for k,v in cls.attributes.iteritems():
            if k.find(".") == -1:
                order_bys_no_fk[k] = v
            else:
                order_bys_no_fk[k.split(".")[1]] = v
        return order_bys_no_fk

    @staticmethod
    def generate_fake(count=20):
        import forgery_py
        from sqlalchemy.exc import IntegrityError
        for i in range(count):
            c = Company(name=forgery_py.lorem_ipsum.word(),
                        symbol=Company.generate_symbol()
                        )
            db.session.add(c)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def update(j):
        passed_keys = j.keys()
        symbol = j.get('symbol')
        if not symbol:
            current_app.logger.debug("No symbol found in JSON: {}".format(j))
            return False

        bind_params = {}
        realized_params = {}
        mapper = inspect(Company)
        for col in mapper.attrs.keys():
            if col not in Company.ignore_attrs and col in passed_keys:
                bind_params[col] = bindparam(col)
                realized_params[col] = j.get(col)

        if not Company.validate_company_values(realized_params):
            current_app.logger.debug("Failed to validate company values: {}".format(j))
            return False

        company_table = mapper.mapped_table
        stmt = company_table.update().where(company_table.c.symbol == symbol).values(**bind_params)
        db.session.execute(stmt, realized_params)
        db.session.commit()
        return Company.query.filter(Company.symbol == symbol).first()


    def dates_to_json(self):
        """

        Returns: a list object that can be converted to json

        """
        indicators = Indicators.query.join(Company).filter_by(id=self.id).all()
        for i in indicators:
            print i.date
        return [indicator.date.strftime("%Y-%m-%d") for indicator in indicators]

    def to_json(self):
        company = {}
        for k,v in self.attributes.iteritems():
            company[k] = getattr(self, k)

        company['id'] = self.id

        return company

    @staticmethod
    def from_json(j):
        company = {}
        for k, v in Company.attributes.iteritems():
            company[k] = j.get(k)

        # name = j.get('name')
        # symbol = j.get('symbol')
        exchange = j.get('exchange')

        if not Company.validate_name(company['name']):
            raise ValueError('Invalid name')

        if not Company.validate_symbol(company['symbol']):
            raise ValueError('Invalid symbol')

        # Use company validation for the index name too
        clean_exchange = Exchange.get_exchange(exchange)

        company['active'] = j.get('active') if j.get('active') else True

        c = Company(**company)
        if clean_exchange:
            c.exchanges.append(clean_exchange)

        return c

    @staticmethod
    def validate_company_values(values):
        """

        Args:
            d: dictionary of Company attributes

        Returns:
            True if valid, false if not

        """
        d = values.copy()
        symbol = d.get('symbol')
        if symbol:
            d.pop('symbol')
            if not Company.validate_symbol(symbol):
                current_app.logger.debug("Failed to validate symbol: {}".format(values))
                return False

        for key in d.keys():
            value = d.get(key)
            if not Company.validate_name(value):
                current_app.logger.debug("Failed to validate name: {}".format(values))
                return False

        return True


    @staticmethod
    def validate_symbol(symbol):
        if not symbol:
            return False

        match = re.match(current_app.config['VALID_COMPANY_SYMBOL'], symbol)
        return True if match else False

    @staticmethod
    def validate_name(name):
        if not name:
            return False

        match = re.match(current_app.config['VALID_COMPANY_NAME'], name)
        return True if match else False

    @staticmethod
    def load_json(data):
        companies = json.loads(data).get('company')
        for company in companies:
            c = Company.from_json(company)
            db.session.add(c)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return "<{cls}|Symbol: {symbol}, Name: {company}>".format(cls=self.__class__, symbol=self.symbol, company=self.name)


class Indicators(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    roe = db.Column(db.Float, nullable=True)
    fcf = db.Column(db.Float, nullable=True)
    ev2ebitda = db.Column(db.Float, nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    attributes = {
        'Company.symbol': "Ticker",
        'roe': "ROE (%)",
        'fcf': "Free Cash Flow",
        'ev2ebitda': "EV/EBITDA",
    }
    ignore_attrs = ['id', 'company_id']
    UniqueConstraint(date, company_id, name="one_per_company_per_day")

    @classmethod
    def get_attributes(cls, with_symbol=True):
        """
        Return all attributes of the class
        """
        if with_symbol:
            return cls.attributes.keys()
        else:
                return [i for i in Indicators.get_attributes() if i != 'Company.symbol']

    @classmethod
    def get_attributes_no_fk(cls):
        """
        Get all attributes, excluding the foreign keys prefix (ie: company.symbol).

        """
        order_bys = cls.attributes.keys()
        order_bys_no_fk = {}
        for k,v in cls.attributes.iteritems():
            if k.find(".") == -1:
                order_bys_no_fk[k] = v
            else:
                order_bys_no_fk[k.split(".")[1]] = v
        return order_bys_no_fk

    @staticmethod
    def generate_fake(count=10):
        import forgery_py
        from random import random, seed
        from sqlalchemy.exc import IntegrityError

        seed()
        companies = Company.query.all()
        for c in range(1, count):
            date = forgery_py.date.date(True, 0, 1500)

            for company in companies:
                i = Indicators(date=date,
                               roe="{0:.2f}".format(random()*0.5),
                               fcf="{0:.2f}".format(random()*0.5),
                               ev2ebitda="{0:.2f}".format(random()*0.5),
                               company_id = company.id
                               )
                db.session.add(i)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()

    def is_duplicate_of_last(self):
        """
        Check if an indicator is a duplicate of the last collected value
        """
        last_date = self.last_indicator_date_by_company(1)
        if not last_date:
            return False

        i = Indicators.query.filter((Indicators.date == last_date) &
                                    (Indicators.company_id == self.company.id)).first()

        # return Indicators.equal_values(self, i)
        return self == i

    # @staticmethod
    # def equal_values(i1, i2):
    #     """
    #     Check if an indicator has equal values, other than the date.
    #     """
    #     print "compare", i1, i2
    #     attribs = Indicators.get_attributes_no_fk()
    #     for k, v in attribs.iteritems():
    #         if k != "symbol" and k != "ev2ebitda" and k != "id":
    #             if getattr(i1, k) != getattr(i2, k):
    #                 return False
    #
    #     return True

    def __eq__(self, other):
        """
        Check if an indicator has equal values, other than the date.
        """
        attribs = Indicators.get_attributes_no_fk()
        for k, v in attribs.iteritems():
            if k != "symbol" and k != "ev2ebitda":
                if getattr(self, k) != getattr(other, k):
                    return False

        return True

    @staticmethod
    def from_json(json_indicators):
        """

        Args:
            json_indicators: name, symbol, **attributes

            If company does not exist, must provide a name and symbol to create it.

        Returns:
            An Indicator object, with sanitized values

        """
        symbol = json_indicators.get('symbol')

        if not symbol:
            current_app.logger.debug("Indicator's symbol not found.")
            return None

        indicators = Indicators()

        # Get company if it exists, otherwise create it
        if not Company.query.filter_by(symbol=symbol).first():
            name = json_indicators.get('name') or get_name_from_symbol(symbol)
            if not name:
                current_app.logger.debug("Company '{}' does not exist.".format(symbol))
                return None

            company = Company(symbol=symbol, name=name)
            db.session.add(company)
            db.session.commit()
        else:
            company = Company.query.filter_by(symbol=symbol).first()

        # Go through each key and assign it, with some exceptions
        for key in json_indicators.keys():
            if key.find(".") == -1 and \
                            key != 'name' and \
                            key != 'symbol' and \
                            key != "company_id" and \
                            key != "id":
                value = float_or_none(json_indicators.get(key))
                column = getattr(Indicators, key)
                if value:
                    print "setting value ", value
                    setattr(indicators, key, value)
                else:
                    print "value not set"
                    # If we didn't get the correct value type for a float, use a placeholder
                    if isinstance(column.type, Float):
                        print "didn't get a float for", column, key, value
                        setattr(indicators, key, -999999999999.99)
                    else:
                        setattr(indicators, key, json_indicators.get(key))

        indicators.company = company
        print "Indicators exiting", indicators, indicators.ev2ebitda

        return indicators

    @staticmethod
    def last_indicator_date():
        try:
            return db.session.query(Indicators.date).order_by(desc("date")).distinct().limit(2).all()[0].date
        except IndexError:
            return None

    def last_indicator_date_by_company(self, index=0, limit=2):
        """

        Args:
            index: date to return (0 is the last date, 1 second to last, etc.  must be less than limit
            limit: maximum number of records to return

        Returns:
            A date, if it exists

        """
        try:
            val = Indicators.query.join(Company).filter(Company.symbol == self.company.symbol).with_entities(Indicators.date).order_by(desc("date")).limit(limit).all()[index].date
            return val
        except AttributeError:
            # indicator has no associated company?
            current_app.logger.debug("No company associated with Indicator?")
            return None
        except IndexError:
            current_app.logger.debug("Index error looking up Indicator")
            return None
        except IntegrityError as e:
            current_app.logger.debug("Integrity Error {}".format(e))
            print "roll it back!"
            db.session.rollback()
            return False

        return None

    def to_json(self):
        indicators = {}
        for k,v in self.get_attributes_no_fk().iteritems():
            if k == "symbol":
                indicators[k] = self.company.symbol
            else:
                indicators[k] = getattr(self, k)

        indicators['id'] = self.id
        indicators['date'] = self.date.isoformat()

        return indicators

    @staticmethod
    def load_json(data):
        indicators = json.loads(data).get('indicators')
        for indicator in indicators:
            i = Indicators.from_json(indicator)
            if i:
                db.session.add(i)
            else:
                continue

            # db.session.add(i)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return "<{cls}|Symbol: {symbol}, Date: {date}>".format(cls=self.__class__,
                                                               symbol=self.company.symbol,
                                                               date=self.date)


#class Sector(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(50), unique=True, nullable=False)
#    siccode = db.Column(db.Integer, unique=True, nullable=False)
#
#    def __repr__(self):
#        return "<{cls}|Sector: {name}, SIC code: {siccode}>".format(cls=self.__class__, name=name, siccode=siccode)
#
#
#class Industry(db.Model):

