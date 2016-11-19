import logging
from app.external.companies import get_sic_code, get_sector_and_industry
from app import db
from app.models import Company, Indicators

logger = logging.getLogger('populate')


def get_company_sics():

    companies = Company.query.filter(Company.sic_code == None)
    for company in companies:
        sic_code = get_sic_code(company.symbol)
        company.sic_code = sic_code

        try:
            db.session.add(company)
            db.session.commit()
        except IntegrityError as e:
            logger.warning(e)
            db.session.rollback()


def get_sectors_and_industries():
    companies = Company.query.filter((Company.industry == None) | (Company.sector == None)).all()
    logger.info("Getting data for {} companies".format(len(companies)))
    for company in companies:
        sector_and_industry = get_sector_and_industry(company.symbol)

        logger.debug("Fetching {}".format(company.symbol))
        if not sector_and_industry:
            continue
        else:
            company.sector = sector_and_industry.get('sector')
            company.industry = sector_and_industry.get('industry')

        try:
            db.session.add(company)
            db.session.commit()
        except IntegrityError as e:
            logger.warning(e)
            db.session.rollback()