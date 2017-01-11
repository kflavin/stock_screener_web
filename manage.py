import json
import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include="app/*")
    COV.start()

import datetime

from app.models import User, Role, Company, Indicators, Exchange
from app import create_app, db

# from populate_indicators import get_ratio_data
# from populate_companies import get_company_details
# from populate import get_company_sics, get_sectors_and_industries
# from app.external.companies import get_sic_code, get_sector_and_industry

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)
manager = Manager(app)

# configure shell and migration commands
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Company=Company, Indicators=Indicators, Exchange=Exchange)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


@manager.command
def test(coverage=False, pattern="test", quiet=True):
    """Runs the unit tests without coverage."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest

    loader = unittest.TestLoader()
    loader.testMethodPrefix = pattern

    tests = loader.discover('tests')
    result = unittest.TextTestRunner(verbosity=2, buffer=quiet).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print('Coverage summary')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        COV.erase()

    #if result.wasSuccessful():
    #    return 0
    #else:
    #    return 1


@manager.command
def cov():
    """Runs the unit tests with coverage."""
    cov = coverage.coverage(branch=True, include='project/*')
    cov.start()
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    cov.stop()
    cov.save()
    print('Coverage Summary:')
    cov.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, 'tmp/coverage')
    cov.html_report(directory=covdir)
    print('HTML version: file://%s/index.html' % covdir)
    cov.erase()


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@manager.command
def create_admin():
    """Creates the admin user."""
    admin = db.session.query(User).filter_by(email="root2").first()
    
    if admin:
        admin.active = True
        admin.confirmed_at = datetime.datetime.utcnow()
        db.session.add(admin)
    else:
        db.session.add(User(email="root2", password="password", active=True, confirmed_at=datetime.datetime.utcnow()))

    db.session.commit()


@manager.command
def make_data():
    """
    Generate some fake data
    """
    Company.generate_fake(3000)
    Indicators.generate_fake(500)

# @manager.command
# def get_ratios():
#     """
#     Pull financial ratios
#     """
#     get_ratio_data()
#
# @manager.command
# def get_companies(throttle=True, index="NYSE", count=-1):
#     """
#     Pull company data
#     """
#     get_company_details(throttle=throttle, exchange=index, count=int(count))


# @manager.command
# def get_sics(symbol=""):
#     """
#
#     Args:
#         symbol: company ticker symbol
#
#     Returns:
#
#     """
#     if symbol:
#         print get_sic_code(symbol)
#     else:
#         get_company_sics()

# @manager.command
# def get_sectors(symbol=""):
#     """
#
#     Args:
#         symbol: company ticker symbol
#
#     Returns:
#
#     """
#     if symbol:
#         print get_sector_and_industry(symbol)
#     else:
#         get_sectors_and_industries()

@manager.command
def create_fixtures(model):
    """

    Args:
        model: company|indicators

    Returns: None
    """

    if model != "company":
        model = "indicators"

    models = {"company": Company, "indicators": Indicators}

    d = {model: []}
    objs = models[model].query.all()
    for i in objs:
        d[model].append(i.to_json())

    with open("app/fixtures/{}.json".format(model), "w") as f:
        f.write(json.dumps(d))


@manager.command
def deploy():
    from flask.ext.migrate import upgrade
    upgrade()


if __name__ == '__main__':
    manager.run()
