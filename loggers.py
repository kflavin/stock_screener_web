import logging

loggers = {
    'app.external.companies': 'DEBUG',
    'populate': 'DEBUG',
}

for k, v in loggers.iteritems():
    logger = logging.getLogger(k)
    logger.setLevel(v)
    logger.addHandler(logging.StreamHandler())