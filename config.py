import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    #WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    BCRYPT_LOG_ROUNDS = 13
    TOKEN_EXPIRATION_IN_SECONDS = 86400

    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECURITY_CONFIRMABLE = True
    SECURITY_TRACKABLE = False

    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTRATION_EMAIL = True
    SECURITY_RECOVERABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_PASSWORD_HASH = os.environ.get('SECURITY_PASSWORD_HASH')
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get("MAIL_USER")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_SENDER = os.environ.get('MAIL_SENDER')

    COMPANIES_PER_PAGE = 25
    INDICATORS_PER_PAGE = 25

    VALID_COMPANY_NAME = "^[0-9a-zA-Z ._'!&$%,-]+$"
    VALID_COMPANY_SYMBOL = "^[A-Z]{0,8}$"

    EDGAR_APP_KEY = os.environ.get('EDGAR_APP_KEY')

    SSL_DISABLE = True

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    WTF_CSRF_ENABLED = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    DEBUG = True
    TOKEN_EXPIRATION_IN_SECONDS = 1
    PRESERVE_CONTEXT_ON_EXCEPTION = False   # For "AssertionError: Popped wrong app context"

    # @classmethod
    # def init_app(cls, app):
    #     import logging
    #     from logging import StreamHandler
    #     handler = StreamHandler()
    #     handler.setLevel(logging.DEBUG)
    #     app.logger.addHandler(handler)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    @staticmethod
    def init_app(app):
        import loggers


class Production(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-prod.sqlite')


class HerokuConfig(Production):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))

    @classmethod
    def init_app(cls, app):
        import logging
        from logging import StreamHandler
        handler = StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)

        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


config = {'development': DevelopmentConfig,
          'testing': TestingConfig,
          'production': Production,
          'default': DevelopmentConfig,
          'heroku': HerokuConfig
          }
