from ..models import Company, Indicators
from .. import db
from sqlalchemy import func


def get_averages(type, search):
    """
    Return a dictionary with averages for each indicator in the given sector
    Args:
        type: sector or industry
        search: search string

    Returns: dict of averages with indicator as key

    """
    # entities to display for averages
    entities = get_entities(with_symbol=False)
    wrapped_entities = []
    for entity in entities:
        wrapped_entities.append(func.avg(entity).label(entity.key))

    averages_d = {}
    if search is not None:
        stmt1 = db.session.query(Indicators.company_id, func.max(Indicators.id).label('max_id')).group_by(
            Indicators.company_id
        ).subquery()
        stmt2 = db.session.query(Company, stmt1.c.max_id).join(stmt1, stmt1.c.company_id == Company.id).filter(
            getattr(Company, type) == search
        )
        count = stmt2.count()
        stmt2 = stmt2.subquery()
        averages = db.session.query(*wrapped_entities). \
            join(stmt2, stmt2.c.max_id == Indicators.id). \
            filter((Indicators.roe != None) & (Indicators.fcf != None) & (Indicators.ev2ebitda != None)). \
            first()

        # from sqlalchemy.dialects import postgresql
        # print str(db.session.query(*wrapped_entities).
        #     join(stmt2, stmt2.c.max_id == Indicators.id).
        #     filter((Indicators.roe != None) & (Indicators.fcf != None) & (Indicators.ev2ebitda != None)).statement.compile(dialect=postgresql.dialect()))

        for e in entities:
            averages_d[e.key] = getattr(averages, e.key)

        averages_d['count'] = count

    return averages_d


def get_entities(with_symbol=True, with_date=False):
    order_bys = Indicators.get_attributes(with_symbol=with_symbol)

    # configure models (for determining column model) and entities (for retrieving columns)
    entities = []
    models = []
    for o in order_bys:
        if o.find(".") != -1:
            entities.append(eval(o))
            models.append(o.split(".")[0])
        else:
            entities.append(eval("Indicators." + o))
    if with_date:
        entities.append(Indicators.date)

    return entities