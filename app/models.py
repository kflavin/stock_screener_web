from flask.ext.security import UserMixin, RoleMixin
from flask.ext.sqlalchemy import SQLAlchemy
from app import db
from random import seed, choice
from string import ascii_uppercase


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
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)

    def __repr__(self):
        return "<Userid: {0}, Email: {1}>".format(self.id, self.email)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    symbol = db.Column(db.String(20), nullable=False, unique=True)
    indicators = db.relationship('Indicators', backref='company', lazy='dynamic')

    @staticmethod
    def generate_symbol():
        seed()
        symbol = ""
        sym_len = int(choice("34")) + 1
        for i in range(1,sym_len):
            symbol += choice(ascii_uppercase)

        return symbol
            

    @staticmethod
    def generate_fake(count=100):
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

    def __repr__(self):
        return "<{cls}|Symbol: {symbol}, Name: {company}>".format(cls=self.__class__, symbol=self.symbol, company=self.name)


class Indicators(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    roe = db.Column(db.Float)
    fcf = db.Column(db.Float)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    @staticmethod
    def generate_fake(count=10):
        import forgery_py
        from random import random, seed
        from sqlalchemy.exc import IntegrityError
        from datetime import datetime

        seed()
        companies = Company.query.all()
        for c in range(1, count):
            date = forgery_py.date.date(True, 0, 1500)

            for company in companies:
                i = Indicators(date=date,
                               roe = "{0:.2f}".format(random()*0.5),
                               fcf = "{0:.2f}".format(random()*0.5),
                               company_id = company.id
                               )
                db.session.add(i)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()

    def __repr__(self):
        return "<{cls}|Symbol: {symbol}, Date: {date}>".format(cls=self.__class__, symbol=self.company.symbol, date=self.date)

